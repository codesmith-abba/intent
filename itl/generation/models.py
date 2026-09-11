from dataclasses import dataclass, field
from enum import Enum
from typing import Any


@dataclass(frozen=True, slots=True)
class GenerationContext:
    """Normalized compiler information required by one generation unit."""

    unit_id: str
    unit_type: str
    intent: str | None = None
    constraints: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    target: str | None = None
    framework: str | None = None
    existing_output: str | None = None
    metadata: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """Stable internal request passed from the compiler to a provider."""

    context: GenerationContext
    requested_unit: str


class GenerationStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    CACHED = "cached"


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """Structured result of one generation attempt."""

    unit_id: str
    status: GenerationStatus
    output: str | None = None
    provider: str | None = None
    model: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
