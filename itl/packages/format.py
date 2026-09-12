from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile

from .errors import InvalidPackageError, PackageIntegrityError
from .models import PackageManifest

MANIFEST_NAME = "manifest.json"


def _safe_member(name: str) -> str:
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts:
        raise InvalidPackageError(f"Unsafe package path: {name!r}.")
    normalized = str(path)
    if normalized in (".", "") or normalized.startswith("/"):
        raise InvalidPackageError(f"Unsafe package path: {name!r}.")
    return normalized


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class PackageReader:
    """Reads and verifies .itlpkg archives without executing their contents."""

    def read_manifest(self, package_path: str | Path) -> PackageManifest:
        path = Path(package_path)
        try:
            with ZipFile(path, "r") as archive:
                names = [_safe_member(info.filename) for info in archive.infolist()]
                if MANIFEST_NAME not in names:
                    raise InvalidPackageError("Package does not contain manifest.json.")
                raw = archive.read(MANIFEST_NAME)
        except (OSError, ValueError) as error:
            raise InvalidPackageError(f"Cannot read package '{path}'.") from error
        try:
            data = json.loads(raw.decode("utf-8"))
            return PackageManifest.from_mapping(data)
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise InvalidPackageError(f"Invalid package manifest in '{path}'.") from error

    def verify(self, package_path: str | Path) -> PackageManifest:
        path = Path(package_path)
        manifest = self.read_manifest(path)
        expected = dict(manifest.files)
        try:
            with ZipFile(path, "r") as archive:
                actual_names = {_safe_member(info.filename) for info in archive.infolist()}
                actual_names.discard(MANIFEST_NAME)
                if actual_names != set(expected):
                    missing = sorted(set(expected) - actual_names)
                    unexpected = sorted(actual_names - set(expected))
                    raise PackageIntegrityError(
                        f"Package file set mismatch; missing={missing}, unexpected={unexpected}."
                    )
                for name, digest in expected.items():
                    actual = sha256_bytes(archive.read(name))
                    if actual != digest:
                        raise PackageIntegrityError(
                            f"Integrity check failed for package file '{name}'."
                        )
        except PackageIntegrityError:
            raise
        except (OSError, ValueError) as error:
            raise InvalidPackageError(f"Cannot verify package '{path}'.") from error
        return manifest

    def archive_sha256(self, package_path: str | Path) -> str:
        return sha256_file(Path(package_path))

    def extract_verified(self, package_path: str | Path, destination: str | Path) -> PackageManifest:
        manifest = self.verify(package_path)
        destination_path = Path(destination)
        destination_path.mkdir(parents=True, exist_ok=True)
        with ZipFile(Path(package_path), "r") as archive:
            for info in archive.infolist():
                name = _safe_member(info.filename)
                if name == MANIFEST_NAME:
                    continue
                target = destination_path / Path(name)
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info, "r") as source, target.open("wb") as output:
                    output.write(source.read())
        return manifest


class PackageBuilder:
    """Builds deterministic package files from already trusted source files."""

    def build(
        self,
        source_root: str | Path,
        manifest: PackageManifest,
        output: str | Path,
    ) -> Path:
        root = Path(source_root).resolve()
        if not root.is_dir():
            raise InvalidPackageError(f"Package source root does not exist: {root}.")

        files: dict[str, str] = {}
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            _safe_member(relative)
            files[relative] = sha256_file(path)

        complete = PackageManifest(
            name=manifest.name,
            version=manifest.version,
            package_type=manifest.package_type,
            plugin=manifest.plugin,
            dependencies=manifest.dependencies,
            entry_module=manifest.entry_module,
            entry_attribute=manifest.entry_attribute,
            format_version=manifest.format_version,
            files=tuple(sorted(files.items())),
            metadata=manifest.metadata,
        )
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".tmp", delete=False) as temp:
            temp_path = Path(temp.name)
        try:
            with ZipFile(temp_path, "w", ZIP_DEFLATED) as archive:
                archive.writestr(MANIFEST_NAME, json.dumps(complete.to_mapping(), sort_keys=True, separators=(",", ":")))
                for relative in sorted(files):
                    archive.write(root / relative, relative)
            os.replace(temp_path, destination)
        finally:
            if temp_path.exists():
                temp_path.unlink()
        return destination
