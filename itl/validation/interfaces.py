from __future__ import annotations

from typing import Protocol

from itl.validation.models import ValidationContext, ValidationResult


class Validator(Protocol):
    """Stable contract for a composable output validator."""

    @property
    def name(self) -> str:
        ...

    def validate(self, context: ValidationContext) -> ValidationResult:
        ...
