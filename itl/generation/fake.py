"""Deterministic provider for compiler tests and offline development."""

from __future__ import annotations

from dataclasses import dataclass, field

from itl.generation.models import GenerationRequest
from itl.generation.provider import ProviderResponse


@dataclass(slots=True)
class FakeGenerationProvider:
    """A predictable provider that never performs network I/O."""

    output: str = "fake generated output"
    provider: str = "fake"
    model: str = "fake-model"
    calls: list[tuple[GenerationRequest, str]] = field(default_factory=list)

    def generate(self, request: GenerationRequest, prompt: str) -> ProviderResponse:
        self.calls.append((request, prompt))
        return ProviderResponse(
            output=self.output,
            provider=self.provider,
            model=self.model,
            metadata={"deterministic": True},
        )
