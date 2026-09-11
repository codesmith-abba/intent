from dataclasses import dataclass, field
from typing import Any

from itl.generation.models import GenerationRequest
from itl.validation.models import ValidationReport


@dataclass(frozen=True, slots=True)
class RepairContext:
    """All normalized information needed to repair one failed build unit."""

    request: GenerationRequest
    generated_output: str
    validation_report: ValidationReport
    dependencies: tuple[str, ...] = ()
    target: str | None = None
    framework: str | None = None
    constraints: tuple[str, ...] = ()
    metadata: tuple[tuple[str, Any], ...] = ()

    @property
    def unit_id(self) -> str:
        return self.request.requested_unit


@dataclass(frozen=True, slots=True)
class RepairRequest:
    context: RepairContext
    attempt: int


@dataclass(frozen=True, slots=True)
class RepairResult:
    unit_id: str
    attempt: int
    status: str
    output: str | None = None
    provider: str | None = None
    model: str | None = None
    error: str | None = None
    validation_report: ValidationReport | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def succeeded(self) -> bool:
        return self.status == "success"


@dataclass(frozen=True, slots=True)
class RepairPolicy:
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if self.max_attempts < 0:
            raise ValueError("max_attempts must be non-negative.")
