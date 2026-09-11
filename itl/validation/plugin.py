from __future__ import annotations

from collections.abc import Callable

from itl.generation.models import GenerationRequest
from itl.plugins.registry import PluginManager
from itl.plugins.models import PluginValidationStatus
from itl.validation.models import (
    ValidationContext,
    ValidationIssue,
    ValidationResult,
    ValidationStatus,
)


class PluginValidator:
    """Adapter that exposes an ITL plugin validation hook as a core validator."""

    def __init__(
        self,
        plugin_manager: PluginManager,
        request_factory: Callable[[ValidationContext], GenerationRequest],
    ):
        self.plugin_manager = plugin_manager
        self.request_factory = request_factory

    @property
    def name(self) -> str:
        return "plugin"

    def validate(self, context: ValidationContext) -> ValidationResult:
        request = self.request_factory(context)
        result = self.plugin_manager.validate(request, str(context.output))
        if result.status == PluginValidationStatus.FAILED:
            issues = tuple(
                ValidationIssue(
                    validator=self.name,
                    message=message,
                    code="plugin_validation_error",
                )
                for message in result.errors
            )
            return ValidationResult(
                unit_id=context.unit_id,
                validator=self.name,
                status=ValidationStatus.FAILED,
                issues=issues,
            )
        status = (
            ValidationStatus.PASSED
            if result.status == PluginValidationStatus.PASSED
            else ValidationStatus.SKIPPED
        )
        return ValidationResult(
            unit_id=context.unit_id,
            validator=self.name,
            status=status,
        )
