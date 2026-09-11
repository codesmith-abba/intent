from __future__ import annotations

from itl.validation.models import ValidationReport


class ValidationFailure(Exception):
    """Raised when generated output fails validation."""

    def __init__(self, report: ValidationReport):
        self.report = report
        messages = "; ".join(issue.message for issue in report.issues)
        super().__init__(messages or f"Validation failed for '{report.unit_id}'.")
