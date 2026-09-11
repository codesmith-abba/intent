from __future__ import annotations

from typing import Protocol

from itl.generation.models import GenerationRequest
from itl.generation.provider import ProviderResponse
from itl.plugins.models import PluginConfig, PluginMetadata, PluginValidationResult


class ITLPlugin(Protocol):
    """Base contract implemented by every ITL plugin."""

    @property
    def metadata(self) -> PluginMetadata:
        ...

    def configure(self, config: PluginConfig) -> None:
        ...


class GenerationPlugin(Protocol):
    """Optional generation capability owned by a plugin."""

    def generate(
        self,
        request: GenerationRequest,
        prompt: str,
    ) -> ProviderResponse:
        ...


class ValidationPlugin(Protocol):
    """Optional output validation capability owned by a plugin."""

    def validate(
        self,
        request: GenerationRequest,
        output: str,
    ) -> PluginValidationResult:
        ...


class InstallationPlugin(Protocol):
    """Future plugin installation hook."""

    def install(self, config: PluginConfig) -> None:
        ...


class UpgradePlugin(Protocol):
    """Future plugin upgrade hook."""

    def upgrade(self, config: PluginConfig) -> None:
        ...
