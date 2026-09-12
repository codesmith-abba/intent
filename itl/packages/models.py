from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from itl.plugins.models import PLUGIN_API_VERSION, PluginMetadata


PACKAGE_FORMAT_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class PackageDependency:
    name: str
    constraint: str = "*"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Package dependency name must not be empty.")
        if not self.constraint.strip():
            raise ValueError("Package dependency constraint must not be empty.")


@dataclass(frozen=True, slots=True)
class PackageManifest:
    name: str
    version: str
    package_type: str = "plugin"
    plugin: PluginMetadata | None = None
    dependencies: tuple[PackageDependency, ...] = ()
    entry_module: str | None = None
    entry_attribute: str = "plugin"
    format_version: str = PACKAGE_FORMAT_VERSION
    files: tuple[tuple[str, str], ...] = ()
    metadata: tuple[tuple[str, Any], ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Package name must not be empty.")
        if not self.version.strip():
            raise ValueError("Package version must not be empty.")
        if self.format_version != PACKAGE_FORMAT_VERSION:
            raise ValueError(f"Unsupported package format version: {self.format_version}.")
        if self.package_type == "plugin" and self.plugin is None:
            raise ValueError("Plugin packages must declare plugin metadata.")
        if self.plugin is not None and self.plugin.api_version != PLUGIN_API_VERSION:
            raise ValueError(f"Unsupported plugin API version: {self.plugin.api_version}.")
        if self.package_type == "plugin" and not self.entry_module:
            raise ValueError("Plugin packages must declare entry_module.")

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "PackageManifest":
        plugin_data = data.get("plugin")
        plugin = None
        if plugin_data is not None:
            plugin = PluginMetadata(
                name=plugin_data["name"],
                version=plugin_data["version"],
                api_version=plugin_data.get("api_version", PLUGIN_API_VERSION),
                targets=tuple(plugin_data.get("targets", ())),
                frameworks=tuple(plugin_data.get("frameworks", ())),
                min_compiler_version=plugin_data.get("min_compiler_version", "1.0"),
                max_compiler_version=plugin_data.get("max_compiler_version"),
                capabilities=tuple(plugin_data.get("capabilities", ())),
            )
        dependencies = tuple(
            PackageDependency(item["name"], item.get("constraint", "*"))
            for item in data.get("dependencies", ())
        )
        files = tuple(sorted((str(path), str(digest)) for path, digest in data.get("files", {}).items()))
        entry = data.get("entry_point") or {}
        metadata = tuple(sorted((str(k), v) for k, v in data.get("metadata", {}).items()))
        return cls(
            name=data["name"],
            version=data["version"],
            package_type=data.get("type", "plugin"),
            plugin=plugin,
            dependencies=dependencies,
            entry_module=entry.get("module"),
            entry_attribute=entry.get("attribute", "plugin"),
            format_version=data.get("format_version", PACKAGE_FORMAT_VERSION),
            files=files,
            metadata=metadata,
        )

    def to_mapping(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "format_version": self.format_version,
            "name": self.name,
            "version": self.version,
            "type": self.package_type,
            "dependencies": [
                {"name": dependency.name, "constraint": dependency.constraint}
                for dependency in self.dependencies
            ],
            "files": dict(self.files),
            "metadata": dict(self.metadata),
        }
        if self.plugin is not None:
            result["plugin"] = {
                "name": self.plugin.name,
                "version": self.plugin.version,
                "api_version": self.plugin.api_version,
                "targets": list(self.plugin.targets),
                "frameworks": list(self.plugin.frameworks),
                "min_compiler_version": self.plugin.min_compiler_version,
                "max_compiler_version": self.plugin.max_compiler_version,
                "capabilities": list(self.plugin.capabilities),
            }
        if self.entry_module is not None:
            result["entry_point"] = {
                "module": self.entry_module,
                "attribute": self.entry_attribute,
            }
        return result


@dataclass(frozen=True, slots=True)
class ResolvedPackage:
    manifest: PackageManifest
    source: str


@dataclass(frozen=True, slots=True)
class InstalledPackage:
    name: str
    version: str
    path: str
    trusted: bool = False
    package_sha256: str = ""
    dependencies: tuple[PackageDependency, ...] = field(default_factory=tuple)
