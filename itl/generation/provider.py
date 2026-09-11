from dataclasses import dataclass, field
from typing import Any, Protocol

from itl.generation.models import GenerationRequest


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    output: str
    provider: str
    model: str
    metadata: dict[str, Any] = field(default_factory=dict)


class GenerationProvider(Protocol):
    """Provider boundary used by the compiler generation backend."""

    def generate(
        self,
        request: GenerationRequest,
        prompt: str,
    ) -> ProviderResponse:
        ...
