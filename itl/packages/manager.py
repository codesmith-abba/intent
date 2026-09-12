from __future__ import annotations

import importlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from itl.plugins.registry import PluginRegistry

from .errors import (
    PackageInstalledError,
    PackageNotFoundError,
    PackageTrustError,
)
from .format import PackageReader, sha256_file
from .models import InstalledPackage, PackageDependency
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
        plan = PackageResolver(self.registry, self.compiler_version).resolve(
            manifest.name,
            f"={manifest.version}",
        )
        source_sha256 = self.reader.archive_sha256(path)
        for dependency in plan:
            if dependency.manifest.name.casefold() != manifest.name.casefold():
                self.install(dependency.source)

        destination = self.cache_root / manifest.name / manifest.version
        if destination.exists():
            existing = self._get(manifest.name, manifest.version)
            if existing is not None and existing.package_sha256 == source_sha256 and self.verify(manifest.name, manifest.version):
                return existing
            raise PackageInstalledError(
                f"Package '{manifest.name}@{manifest.version}' is already installed with different contents."
            )

        destination.mkdir(parents=True, exist_ok=False)
        try:
            self.reader.extract_verified(path, destination)
            shutil.copy2(path, destination / "package.itlpkg")
            record = InstalledPackage(
                name=manifest.name,
                version=manifest.version,
                path=str(destination),
                trusted=False,
                package_sha256=source_sha256,
                dependencies=manifest.dependencies,
            )
            self._set(record)
            return record
        except Exception:
            if destination.exists():
                _remove_tree(destination)
            raise

    def upgrade(self, name: str) -> InstalledPackage:
        current = self.latest_installed(name)
        candidates = [
            candidate
            for candidate in self.registry.candidates(name)
            if Version.parse(candidate.manifest.version) > Version.parse(current.version)
            and all(
                satisfies(candidate.manifest.version, dependency.constraint)
                for installed in self.installed()
                for dependency in installed.dependencies
                if dependency.name.casefold() == name.casefold()
                and installed.name.casefold() != name.casefold()
            )
        ]
        if not candidates:
            return current
        return self.install(candidates[0].source)

    def trust(self, name: str, version: str | None = None) -> InstalledPackage:
        record = self._select_installed(name, version)
        self._assert_integrity(record)
        return self._replace(record, trusted=True)

    def untrust(self, name: str, version: str | None = None) -> InstalledPackage:
        return self._replace(self._select_installed(name, version), trusted=False)

    def remove(self, name: str, version: str | None = None) -> None:
        record = self._select_installed(name, version)
        dependents = [
            other.name
            for other in self.installed()
            if other.name.casefold() != record.name.casefold()
            and any(dependency.name.casefold() == record.name.casefold() for dependency in other.dependencies)
            and any(
                dependency.name.casefold() == record.name.casefold()
                and satisfies(record.version, dependency.constraint)
                for dependency in other.dependencies
            )
        ]
        if dependents:
            raise PackageInstalledError(
                f"Cannot remove '{record.name}@{record.version}'; required by {', '.join(sorted(set(dependents)))}."
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
        try:
            package_path = Path(record.path) / "package.itlpkg"
            if not package_path.is_file():
                return False
            if sha256_file(package_path) != record.package_sha256:
                return False
            manifest = self.reader.verify(package_path)
            installed_manifest = json.loads((Path(record.path) / "manifest.json").read_text(encoding="utf-8"))
            if manifest.to_mapping() != installed_manifest:
                return False
            for relative, digest in manifest.files:
                file_path = Path(record.path) / relative
                if not file_path.is_file() or sha256_file(file_path) != digest:
                    return False
            return True
        except Exception:
            return False

    def load_plugin(
        self,
        name: str,
        version: str | None = None,
        plugin_registry: PluginRegistry | None = None,
    ) -> object:
        """Load and register plugin code only after explicit trust and verification."""
        record = self._select_installed(name, version)
        if not record.trusted:
            raise PackageTrustError(
                f"Package '{record.name}@{record.version}' is not trusted; trust it before loading code."
            )
        self._assert_integrity(record)
        manifest = self.reader.verify(Path(record.path) / "package.itlpkg")
        if manifest.package_type != "plugin" or not manifest.entry_module:
            raise PackageNotFoundError(f"Installed package '{record.name}' has no plugin entry point.")

        sys.path.insert(0, record.path)
        try:
            module = importlib.import_module(manifest.entry_module)
            plugin = getattr(module, manifest.entry_attribute)
            if callable(plugin) and not hasattr(plugin, "metadata"):
                plugin = plugin()
        finally:
            sys.path.remove(record.path)

        target_registry = plugin_registry or PluginRegistry(compiler_version=self.compiler_version)
        target_registry.register(plugin)
        return plugin

    def installed(self) -> tuple[InstalledPackage, ...]:
        state = self._read_state()
        records = []
        for item in state:
            dependencies = tuple(
                PackageDependency(
                    dependency["name"], dependency.get("constraint", "*"),
                )
                for dependency in item.get("dependencies", ())
                if isinstance(dependency, dict)
            )
            # Older state entries stored dependency names only; preserve them as unconstrained dependencies.
            dependencies += tuple(
                PackageDependency(dependency)
                for dependency in item.get("dependencies", ())
                if isinstance(dependency, str)
            )
            records.append(
                InstalledPackage(
                    name=item["name"],
                    version=item["version"],
                    path=item["path"],
                    trusted=item.get("trusted", False),
                    package_sha256=item.get("package_sha256", ""),
                    dependencies=dependencies,
                )
            )
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

    def _assert_integrity(self, record: InstalledPackage) -> None:
        if not self.verify(record.name, record.version):
            raise PackageTrustError(
                f"Integrity verification failed for '{record.name}@{record.version}'."
            )

    def _replace(self, record: InstalledPackage, trusted: bool) -> InstalledPackage:
        updated = InstalledPackage(
            name=record.name,
            version=record.version,
            path=record.path,
            trusted=trusted,
            package_sha256=record.package_sha256,
            dependencies=record.dependencies,
        )
        self._set(updated)
        return updated

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
            value = json.loads(self.state_path.read_text(encoding="utf-8"))
            if not isinstance(value, list):
                raise ValueError("State must be a list.")
            return value
        except (OSError, json.JSONDecodeError, ValueError) as error:
            raise PackageInstalledError("Installed package state is invalid.") from error

    def _write_state(self, records: list[InstalledPackage]) -> None:
        data = [
            {
                "name": item.name,
                "version": item.version,
                "path": item.path,
                "trusted": item.trusted,
                "package_sha256": item.package_sha256,
                "dependencies": [
                    {"name": dependency.name, "constraint": dependency.constraint}
                    for dependency in item.dependencies
                ],
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
