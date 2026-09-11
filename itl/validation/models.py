from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ValidationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class ValidationContext:
    """Normalized information supplied to validators for one build unit."""

    unit_id: str
    output: object
    source: str | None = None
    unit_type: str | None = None
    target: str | None = None
    framework: str | None = None
    metadata: tuple[tuple[str, Any], ...] = ()

    def get(self, key: str, default: Any = None) -> Any:
        for name, value in self.metadata:
            if name == key:
                return value
        return default


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    validator: str
    message: str
    code: str = "validation_error"
    severity: str = "error"
    details: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True, slots=True)
class ValidationResult:
    unit_id: str
    validator: str
    status: ValidationStatus
    issues: tuple[ValidationIssue, ...] = ()
    metadata: tuple[tuple[str, Any], ...] = ()

    @property
    def passed(self) -> bool:
        return self.status == ValidationStatus.PASSED

    @property
    def failed(self) -> bool:
        return self.status == ValidationStatus.FAILED


@dataclass(frozen=True, slots=True)
class ValidationReport:
    unit_id: str
    results: tuple[ValidationResult, ...] = ()

    @property
    def passed(self) -> bool:
        return not self.failed

    @property
    def failed(self) -> tuple[ValidationResult, ...]:
        return tuple(result for result in self.results if result.failed)

    @property
    def issues(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for result in self.results for issue in result.issues)

    @property
    def validators_run(self) -> int:
        return len(self.results)


@dataclass(slots=True)
class ValidationSummary:
    """Aggregated reports for a complete build outcome."""

    reports: list[ValidationReport] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failed

    @property
    def failed(self) -> list[ValidationReport]:
        return [report for report in self.reports if not report.passed]

    @property
    def issues(self) -> list[ValidationIssue]:
        return [issue for report in self.reports for issue in report.issues]
