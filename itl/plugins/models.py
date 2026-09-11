from dataclasses import dataclass
from typing import Any


PLUGIN_API_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class PluginMetadata:
    """Stable identity and compatibility information for an ITL plugin."""

    name: str
    version: str
    api_version: str = PLUGIN_API_VERSION
    targets: tuple[str, ...] = ()
    frameworks: tuple[str, ...] = ()
    min_compiler_version: str = "1.0"
    max_compiler_version: str | None = None
    capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Plugin name must not be empty.")
        if not self.version.strip():
            raise ValueError("Plugin version must not be empty.")
        if self.api_version != PLUGIN_API_VERSION:
            raise ValueError(
                f"Unsupported plugin API version: {self.api_version}."
            )


@dataclass(frozen=True, slots=True)
class PluginConfig:
    """Immutable configuration passed to a plugin."""

    values: tuple[tuple[str, Any], ...] = ()

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None = None) -> "PluginConfig":
        if values is None:
            return cls()
        return cls(tuple(sorted(values.items(), key=lambda item: item[0])))

    def get(self, key: str, default: Any = None) -> Any:
        for name, value in self.values:
            if name == key:
                return value
        return default

    def as_dict(self) -> dict[str, Any]:
        return dict(self.values)


class PluginValidationStatus:
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class PluginValidationResult:
    """Structured result returned by a plugin validation hook."""

    status: str
    errors: tuple[str, ...] = ()
    metadata: tuple[tuple[str, Any], ...] = ()

    @property
    def passed(self) -> bool:
        return self.status == PluginValidationStatus.PASSED

    @property
    def failed(self) -> bool:
        return self.status == PluginValidationStatus.FAILED
