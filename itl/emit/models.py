from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class EmitStatus(str, Enum):
    CREATED = "created"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"
    REMOVED = "removed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class EmitResult:
    source: str
    status: EmitStatus
    path: Path | None = None
    error: Exception | None = None


@dataclass(slots=True)
class EmitResults:
    results: list[EmitResult] = field(default_factory=list)

    def add(self, result: EmitResult) -> None:
        self.results.append(result)

    @property
    def created(self) -> list[EmitResult]:
        return [r for r in self.results if r.status == EmitStatus.CREATED]

    @property
    def modified(self) -> list[EmitResult]:
        return [r for r in self.results if r.status == EmitStatus.MODIFIED]

    @property
    def unchanged(self) -> list[EmitResult]:
        return [r for r in self.results if r.status == EmitStatus.UNCHANGED]

    @property
    def removed(self) -> list[EmitResult]:
        return [r for r in self.results if r.status == EmitStatus.REMOVED]

    @property
    def failed(self) -> list[EmitResult]:
        return [r for r in self.results if r.status == EmitStatus.FAILED]

    @property
    def succeeded(self) -> bool:
        return not self.failed
