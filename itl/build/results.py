from dataclasses import dataclass, field
from enum import Enum

from itl.validation.models import ValidationReport


class BuildResultStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(slots=True)
class BuildResult:
    source: str
    status: BuildResultStatus
    output: object | None = None
    error: Exception | None = None
    validation_report: ValidationReport | None = None


@dataclass(slots=True)
class BuildResults:
    results: list[BuildResult] = field(default_factory=list)

    def add(self, result: BuildResult):
        self.results.append(result)

    @property
    def successful(self) -> list[BuildResult]:
        return [result for result in self.results if result.status == BuildResultStatus.SUCCESS]

    @property
    def failed(self) -> list[BuildResult]:
        return [result for result in self.results if result.status == BuildResultStatus.FAILED]

    @property
    def skipped(self) -> list[BuildResult]:
        return [result for result in self.results if result.status == BuildResultStatus.SKIPPED]

    @property
    def succeeded(self) -> bool:
        return not self.failed and not self.skipped
