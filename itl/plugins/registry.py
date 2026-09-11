from __future__ import annotations

import importlib
from importlib import metadata as importlib_metadata
from collections.abc import Iterable
from typing import Any

from itl.generation.models import GenerationRequest
from itl.generation.provider import GenerationProvider, ProviderResponse
from itl.plugins.errors import (
    DuplicatePluginError,
    IncompatiblePluginError,
    InvalidPluginError,
    PluginCapabilityError,
    PluginNotFoundError,
    PluginSelectionError,
)
from itl.plugins.interfaces import GenerationPlugin, ValidationPlugin
from itl.plugins.models import (
    PLUGIN_API_VERSION,
    PluginConfig,
    PluginMetadata,
    PluginValidationResult,
    PluginValidationStatus,
)


COMPILER_VERSION = "1.0"


def _version(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in value.split("."))
    except ValueError as error:
        raise ValueError(f"Invalid version '{value}'.") from error


class PluginRegistry:
    """Registration, discovery, compatibility and target selection."""

    def __init__(self, compiler_version: str = COMPILER_VERSION):
        self.compiler_version = compiler_version
        self._plugins: dict[str, object] = {}

    @property
    def plugins(self) -> tuple[object, ...]:
        return tuple(self._plugins[name] for name in sorted(self._plugins))

    def register(self, plugin: object) -> None:
        metadata = self._metadata_for(plugin)
        self._validate_compatibility(metadata)

        key = metadata.name.casefold()
        if key in self._plugins:
            raise DuplicatePluginError(
                f"Plugin '{metadata.name}' is already registered."
            )
        self._plugins[key] = plugin

    def discover(self, modules: Iterable[str]) -> tuple[object, ...]:
        discovered: list[object] = []
        for module_name in modules:
            module = importlib.import_module(module_name)
            plugin = getattr(module, "plugin", None)
            if plugin is None:
                factory = getattr(module, "create_plugin", None)
                if factory is None or not callable(factory):
                    raise InvalidPluginError(
                        f"Module '{module_name}' does not expose 'plugin' "
                        "or callable 'create_plugin'."
                    )
                plugin = factory()
            self.register(plugin)
            discovered.append(plugin)
        return tuple(discovered)

    def discover_entry_points(self, group: str = "itl.plugins") -> tuple[object, ...]:
        entry_points = importlib_metadata.entry_points()
        if hasattr(entry_points, "select"):
            selected = entry_points.select(group=group)
        else:
            selected = entry_points.get(group, ())

        discovered: list[object] = []
        for entry_point in selected:
            plugin = entry_point.load()
            if callable(plugin) and not hasattr(plugin, "metadata"):
                plugin = plugin()
            self.register(plugin)
            discovered.append(plugin)
        return tuple(discovered)

    def select(
        self,
        target: str | None,
        framework: str | None,
    ) -> object:
        candidates: list[tuple[int, str, object]] = []
        for plugin in self._plugins.values():
            metadata = self._metadata_for(plugin)
            if not self._matches(metadata, target, framework):
                continue
            score = self._score(metadata, target, framework)
            candidates.append((score, metadata.name.casefold(), plugin))

        if not candidates:
            raise PluginNotFoundError(
                f"No plugin is registered for target={target!r}, "
                f"framework={framework!r}."
            )

        candidates.sort(key=lambda item: (-item[0], item[1]))
        best_score = candidates[0][0]
        best = [candidate for candidate in candidates if candidate[0] == best_score]
        if len(best) > 1:
            names = ", ".join(candidate[2].metadata.name for candidate in best)
            raise PluginSelectionError(
                f"Multiple plugins match target={target!r}, "
                f"framework={framework!r}: {names}."
            )
        return candidates[0][2]

    def configure(self, name: str, config: PluginConfig) -> None:
        plugin = self._plugins.get(name.casefold())
        if plugin is None:
            raise PluginNotFoundError(f"Plugin '{name}' is not registered.")
        configure = getattr(plugin, "configure", None)
        if not callable(configure):
            raise InvalidPluginError(
                f"Plugin '{name}' does not implement configure()."
            )
        configure(config)

    def _metadata_for(self, plugin: object) -> PluginMetadata:
        metadata = getattr(plugin, "metadata", None)
        if not isinstance(metadata, PluginMetadata):
            raise InvalidPluginError(
                "Plugin must expose a PluginMetadata instance as 'metadata'."
            )
        for capability in metadata.capabilities:
            if not isinstance(capability, str) or not capability.strip():
                raise InvalidPluginError("Plugin capabilities must be non-empty strings.")
        return metadata

    def _validate_compatibility(self, metadata: PluginMetadata) -> None:
        if metadata.api_version != PLUGIN_API_VERSION:
            raise IncompatiblePluginError(
                f"Plugin '{metadata.name}' requires plugin API "
                f"{metadata.api_version}; supported API is {PLUGIN_API_VERSION}."
            )

        current = _version(self.compiler_version)
        minimum = _version(metadata.min_compiler_version)
        maximum = (
            _version(metadata.max_compiler_version)
            if metadata.max_compiler_version is not None
            else None
        )
        if current < minimum or (maximum is not None and current > maximum):
            raise IncompatiblePluginError(
                f"Plugin '{metadata.name}' is incompatible with compiler "
                f"version {self.compiler_version}."
            )

    @staticmethod
    def _matches(
        metadata: PluginMetadata,
        target: str | None,
        framework: str | None,
    ) -> bool:
        if metadata.targets and (
            target is None or target.casefold() not in {value.casefold() for value in metadata.targets}
        ):
            return False
        if metadata.frameworks and (
            framework is None
            or framework.casefold() not in {value.casefold() for value in metadata.frameworks}
        ):
            return False
        return True

    @staticmethod
    def _score(
        metadata: PluginMetadata,
        target: str | None,
        framework: str | None,
    ) -> int:
        score = 0
        if metadata.targets and target is not None:
            score += 2
        if metadata.frameworks and framework is not None:
            score += 2
        return score


class PluginGenerationProvider:
    """Adapter that lets the existing AIGenerator consume plugin generation."""

    def __init__(self, registry: PluginRegistry):
        self.registry = registry

    def generate(
        self,
        request: GenerationRequest,
        prompt: str,
    ) -> ProviderResponse:
        plugin = self.registry.select(
            request.context.target,
            request.context.framework,
        )
        generate = getattr(plugin, "generate", None)
        if not callable(generate):
            raise PluginCapabilityError(
                f"Plugin '{plugin.metadata.name}' does not provide generation."
            )
        if "generation" not in plugin.metadata.capabilities:
            raise PluginCapabilityError(
                f"Plugin '{plugin.metadata.name}' does not declare generation capability."
            )
        return generate(request, prompt)


class PluginManager:
    """High-level plugin facade used by generation and future validation stages."""

    def __init__(self, registry: PluginRegistry | None = None):
        self.registry = registry or PluginRegistry()

    def generation_provider(self) -> GenerationProvider:
        return PluginGenerationProvider(self.registry)

    def validate(
        self,
        request: GenerationRequest,
        output: str,
    ) -> PluginValidationResult:
        plugin = self.registry.select(
            request.context.target,
            request.context.framework,
        )
        validate = getattr(plugin, "validate", None)
        if not callable(validate) or "validation" not in plugin.metadata.capabilities:
            return PluginValidationResult(
                status=PluginValidationStatus.SKIPPED,
            )
        return validate(request, output)
