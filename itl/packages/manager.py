from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
from pathlib import Path

from itl.plugins.registry import PluginRegistry

from .errors import (
    PackageInstalledError,
    PackageNotFoundError,
    PackageTrustError,
)
from .format import PackageReader
from .models import InstalledPackage
from .registry import LocalPackageRegistry, PackageResolver, Version, satisfies


class PackageManager:
    """Installs package files without executing code until explicitly trusted."""

    def __init__(
        self,
        registry: LocalPackageRegistry,
        cache_root: str | Path,
        compiler_version: str = "1.0",
    ):
        self.registry = registry
        self.cache_root = Path(cache_root)
        self.compiler_version = compiler_version
        self.reader = PackageReader()
        self.state_path = self.cache_root / "state.json"
        self.cache_root.mkdir(parents=True, exist_ok=True)

    def install(self, package_path: str | Path) -> InstalledPackage:
        path = Path(package_path)
        manifest = self.reader.verify(path)
        resolved = self.registry.resolve(
            manifest.name,
            f"={manifest.version}",
            compiler_version=self.compiler_version,
        )
        if not resolved:
            raise PackageNotFoundError(
                f"Package '{manifest.name}@{manifest.version}' is not available in the local registry."
            )
        plan = PackageResolver(self.registry, self.compiler_version).resolve(
            manifest.name,
            f"={manifest.version}",
        )
        for dependency in plan:
            if dependency.manifest.name.casefold() == manifest.name.casefold():
                continue
            self.install(dependency.source)

        destination = self.cache_root / manifest.name / manifest.version
        if destination.exists():
            existing = self._get(manifest.name, manifest.version)
            if existing is not None and existing.package_sha256 == self.reader.archive_sha256(path):
                return existing
            raise PackageInstalledError(
                f"Package '{manifest.name}@{manifest.version}' is already installed with different contents."
            )

        destination.mkdir(parents=True, exist_ok=False)
        try:
            self.reader.extract_verified(path, destination)
            record = InstalledPackage(
                name=manifest.name,
                version=manifest.version,
                path=str(destination),
                trusted=False,
                package_sha256=self.reader.archive_sha256(path),
                dependencies=tuple(dep.name for dep in manifest.dependencies),
            )
            self._set(record)
            return record
        except Exception:
            if destination.exists():
                _remove_tree(destination)
            raise

    def upgrade(self, name: str) -> InstalledPackage:
        current = self.latest_installed(name)
        candidates = self.registry.candidates(name)
        newer = [
            candidate
            for candidate in candidates
            if Version.parse(candidate.manifest.version) > Version.parse(current.version)
        ]
        if not newer:
            return current
        return self.install(newer[0].source)

    def trust(self, name: str, version: str | None = None) -> InstalledPackage:
        record = self._select_installed(name, version)
        updated = InstalledPackage(
            name=record.name,
            version=record.version,
            path=record.path,
            trusted=True,
            package_sha256=record.package_sha256,
            dependencies=record.dependencies,
        )
        self._set(updated)
        return updated

    def untrust(self, name: str, version: str | None = None) -> InstalledPackage:
        record = self._select_installed(name, version)
        updated = InstalledPackage(
            name=record.name,
            version=record.version,
            path=record.path,
            trusted=False,
            package_sha256=record.package_sha256,
            dependencies=record.dependencies,
        )
        self._set(updated)
        return updated

    def remove(self, name: str, version: str | None = None) -> None:
        record = self._select_installed(name, version)
        dependents = [
            other.name
            for other in self.installed()
            if other.name.casefold() != record.name.casefold()
            and record.name.casefold() in {dependency.casefold() for dependency in other.dependencies}
        ]
        if dependents:
            raise PackageInstalledError(
                f"Cannot remove '{record.name}@{record.version}'; required by {', '.join(sorted(dependents))}."
            )
        _remove_tree(Path(record.path))
        records = [
            item
            for item in self.installed()
            if not (item.name.casefold() == record.name.casefold() and item.version == record.version)
        ]
        self._write_state(records)

    def verify(self, name: str, version: str | None = None) -> bool:
        record = self._select_installed(name, version)
        package_path = Path(record.path) / "manifest.json"
        if not package_path.exists():
            return False
        # Recompute every installed payload hash against the recorded manifest.
        from zipfile import ZipFile
        manifest = json.loads(package_path.read_text(encoding="utf-8"))
        expected = manifest.get("files", {})
        for relative, digest in expected.items():
            file_path = Path(record.path) / relative
            if not file_path.is_file() or self.reader.archive_sha256(file_path) == "":
                return False
            from .format import sha256_file
            if sha256_file(file_path) != digest:
                return False
        return True

    def load_plugin(
        self,
        name: str,
        version: str | None = None,
        plugin_registry: PluginRegistry | None = None,
    ) -> object:
        """Load and register plugin code only after explicit trust."""
        record = self._select_installed(name, version)
        if not record.trusted:
            raise PackageTrustError(
                f"Package '{record.name}@{record.version}' is not trusted; trust it before loading code."
            )
        manifest = self.reader.read_manifest(Path(record.path) / "package.itlpkg") if (Path(record.path) / "package.itlpkg").exists() else None
        data = json.loads((Path(record.path) / "manifest.json").read_text(encoding="utf-8"))
        entry = data.get("entry_point") or {}
        module_name = entry.get("module")
        attribute = entry.get("attribute", "plugin")
        if not module_name:
            raise PackageNotFoundError(f"Installed package '{record.name}' has no plugin entry point.")

        sys.path.insert(0, record.path)
        try:
            module = importlib.import_module(module_name)
            plugin = getattr(module, attribute)
            if callable(plugin) and not hasattr(plugin, "metadata"):
                plugin = plugin()
        finally:
            sys.path.remove(record.path)

        target_registry = plugin_registry or PluginRegistry(compiler_version=self.compiler_version)
        target_registry.register(plugin)
        return plugin

    def installed(self) -> tuple[InstalledPackage, ...]:
        state = self._read_state()
        records = [InstalledPackage(**item) for item in state]
        return tuple(sorted(records, key=lambda item: (item.name.casefold(), Version.parse(item.version))))

    def latest_installed(self, name: str) -> InstalledPackage:
        records = [item for item in self.installed() if item.name.casefold() == name.casefold()]
        if not records:
            raise PackageNotFoundError(f"Package '{name}' is not installed.")
        return max(records, key=lambda item: Version.parse(item.version))

    def _select_installed(self, name: str, version: str | None) -> InstalledPackage:
        if version is None:
            return self.latest_installed(name)
        for record in self.installed():
            if record.name.casefold() == name.casefold() and record.version == version:
                return record
        raise PackageNotFoundError(f"Package '{name}@{version}' is not installed.")

    def _get(self, name: str, version: str) -> InstalledPackage | None:
        for record in self.installed():
            if record.name.casefold() == name.casefold() and record.version == version:
                return record
        return None

    def _set(self, record: InstalledPackage) -> None:
        records = [
            item
            for item in self.installed()
            if not (item.name.casefold() == record.name.casefold() and item.version == record.version)
        ]
        records.append(record)
        self._write_state(records)

    def _read_state(self) -> list[dict]:
        if not self.state_path.exists():
            return []
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise PackageInstalledError("Installed package state is invalid.") from error

    def _write_state(self, records: list[InstalledPackage]) -> None:
        data = [
            {
                "name": item.name,
                "version": item.version,
                "path": item.path,
                "trusted": item.trusted,
                "package_sha256": item.package_sha256,
                "dependencies": list(item.dependencies),
            }
            for item in sorted(records, key=lambda item: (item.name.casefold(), Version.parse(item.version)))
        ]
        self.cache_root.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.cache_root, delete=False) as temp:
            json.dump(data, temp, indent=2, sort_keys=True)
            temp.write("\n")
            temp_path = Path(temp.name)
        os.replace(temp_path, self.state_path)


def _remove_tree(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        for child in path.iterdir():
            _remove_tree(child)
        path.rmdir()
    else:
        path.unlink()
