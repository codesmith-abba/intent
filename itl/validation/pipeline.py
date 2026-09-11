from __future__ import annotations

from collections.abc import Iterable

from itl.validation.interfaces import Validator
from itl.validation.models import (
    ValidationContext,
    ValidationIssue,
    ValidationReport,
    ValidationResult,
    ValidationStatus,
)


class ValidatorPipeline:
    """Runs validators in deterministic order and aggregates their results."""

    def __init__(self, validators: Iterable[Validator] = ()):
        self.validators = tuple(validators)
        names = [validator.name for validator in self.validators]
        if any(not name.strip() for name in names):
            raise ValueError("Validator name must not be empty.")
        if len({name.lower() for name in names}) != len(names):
            raise ValueError("Duplicate validators are not allowed.")

    def validate(self, context: ValidationContext) -> ValidationReport:
        results: list[ValidationResult] = []
        for validator in self.validators:
            try:
                result = validator.validate(context)
                if result.unit_id != context.unit_id:
                    raise ValueError(
                        "Validator returned a result for a different build unit."
                    )
                if result.validator != validator.name:
                    raise ValueError(
                        "Validator result name does not match the validator."
                    )
                results.append(result)
            except Exception as error:
                results.append(
                    ValidationResult(
                        unit_id=context.unit_id,
                        validator=validator.name,
                        status=ValidationStatus.FAILED,
                        issues=(
                            ValidationIssue(
                                validator=validator.name,
                                message=str(error) or error.__class__.__name__,
                                code="validator_exception",
                                details=(("exception", error.__class__.__name__),),
                            ),
                        ),
                    )
                )
        return ValidationReport(unit_id=context.unit_id, results=tuple(results))
