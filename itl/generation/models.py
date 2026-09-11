from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from itl.gir.models import GIRNode


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

    @classmethod
    def from_gir(
        cls,
        unit_id: str,
        node: GIRNode,
        dependencies: set[str] | tuple[str, ...] = (),
        existing_output: str | None = None,
    ) -> "GenerationContext":
        """Create context from normalized GIR, never from source text."""
        system = getattr(node, "system", None)
        target = getattr(node, "target", None)
        framework = getattr(node, "framework", None)

        if system is not None:
            target = target or getattr(system, "target", None)
            framework = framework or getattr(system, "framework", None)

        raw_constraints = getattr(node, "constraints", ())
        constraints = tuple(sorted(str(value) for value in raw_constraints))

        return cls(
            unit_id=unit_id,
            unit_type=type(node).__name__,
            intent=node.intent,
            constraints=constraints,
            dependencies=tuple(sorted(dependencies)),
            target=target,
            framework=framework,
            existing_output=existing_output,
        )


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
