from dataclasses import dataclass

from itl.build.models import BuildPlan
from itl.build.results import BuildResults
from itl.build.summary import BuildSummary
from itl.validation.models import ValidationSummary


@dataclass(slots=True)
class BuildOutcome:

    plan: BuildPlan

    results: BuildResults

    summary: BuildSummary

    @property
    def validation(self) -> ValidationSummary | None:
        reports = [
            result.validation_report
            for result in self.results.results
            if result.validation_report is not None
        ]
        return ValidationSummary(reports=reports) if reports else None
