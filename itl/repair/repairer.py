from collections.abc import Callable, Mapping

from itl.build.models import BuildItem
from itl.generation.models import GenerationContext, GenerationRequest
from itl.repair.models import (
    RepairContext,
    RepairPolicy,
    RepairRequest,
    RepairResult,
)
from itl.repair.prompt import RepairPromptBuilder
from itl.repair.provider import RepairProvider
from itl.validation.models import ValidationContext, ValidationReport
from itl.validation.pipeline import ValidatorPipeline


class RepairFailure(RuntimeError):
    """Structured final repair failure."""

    def __init__(self, result: RepairResult):
        self.result = result
        super().__init__(result.error or "Repair failed.")


class AIRepairer:
    """Repairs one failed generated unit and validates every attempt."""

    def __init__(
        self,
        provider: RepairProvider,
        contexts: Mapping[str, GenerationContext],
        validator: ValidatorPipeline,
        policy: RepairPolicy | None = None,
        prompt_builder: RepairPromptBuilder | None = None,
        validation_context_factory: Callable[[BuildItem, object], ValidationContext] | None = None,
    ):
        self.provider = provider
        self.contexts = contexts
        self.validator = validator
        self.policy = policy or RepairPolicy()
        self.prompt_builder = prompt_builder or RepairPromptBuilder()
        self.validation_context_factory = validation_context_factory

    def request_for(
        self,
        item: BuildItem,
        output: str,
        report: ValidationReport,
    ) -> RepairRequest:
        try:
            generation_context = self.contexts[item.source]
        except KeyError as error:
            raise RepairFailure(
                RepairResult(
                    unit_id=item.source,
                    attempt=0,
                    status="failed",
                    error=f"No generation context exists for '{item.source}'.",
                )
            ) from error

        context = RepairContext(
            request=GenerationRequest(
                context=generation_context,
                requested_unit=item.source,
            ),
            generated_output=output,
            validation_report=report,
            dependencies=tuple(sorted(item.dependencies)),
            target=generation_context.target,
            framework=generation_context.framework,
        )
        return RepairRequest(context=context, attempt=1)

    def repair(
        self,
        item: BuildItem,
        output: str,
        report: ValidationReport,
    ) -> RepairResult:
        if report.passed:
            return RepairResult(
                unit_id=item.source,
                attempt=0,
                status="success",
                output=output,
                validation_report=report,
                metadata={"unchanged": True},
            )

        if self.policy.max_attempts == 0:
            return RepairResult(
                unit_id=item.source,
                attempt=0,
                status="failed",
                output=output,
                error="Repair attempts are disabled by policy.",
                validation_report=report,
            )

        request = self.request_for(item, output, report)
        current_output = output
        current_report = report

        for attempt in range(1, self.policy.max_attempts + 1):
            request = RepairRequest(
                context=RepairContext(
                    request=request.context.request,
                    generated_output=current_output,
                    validation_report=current_report,
                    dependencies=request.context.dependencies,
                    target=request.context.target,
                    framework=request.context.framework,
                    constraints=request.context.constraints,
                    metadata=request.context.metadata,
                ),
                attempt=attempt,
            )
            prompt = self.prompt_builder.build(request)
            try:
                response = self.provider.repair(request, prompt)
            except Exception as error:
                return RepairResult(
                    unit_id=item.source,
                    attempt=attempt,
                    status="failed",
                    output=current_output,
                    error=str(error),
                    validation_report=current_report,
                )

            candidate = response.output
            if candidate == current_output:
                return RepairResult(
                    unit_id=item.source,
                    attempt=attempt,
                    status="failed",
                    output=candidate,
                    provider=response.provider,
                    model=response.model,
                    error="Repair provider returned unchanged output.",
                    validation_report=current_report,
                    metadata=dict(response.metadata),
                )

            try:
                if self.validation_context_factory is not None:
                    validation_context = self.validation_context_factory(item, candidate)
                else:
                    validation_context = ValidationContext(
                        unit_id=item.source,
                        source=item.source,
                        output=candidate,
                    )
                current_report = self.validator.validate(validation_context)
            except Exception as error:
                return RepairResult(
                    unit_id=item.source,
                    attempt=attempt,
                    status="failed",
                    output=candidate,
                    provider=response.provider,
                    model=response.model,
                    error=str(error),
                    validation_report=current_report,
                    metadata=dict(response.metadata),
                )

            current_output = candidate
            if current_report.passed:
                return RepairResult(
                    unit_id=item.source,
                    attempt=attempt,
                    status="success",
                    output=current_output,
                    provider=response.provider,
                    model=response.model,
                    validation_report=current_report,
                    metadata=dict(response.metadata),
                )

        return RepairResult(
            unit_id=item.source,
            attempt=self.policy.max_attempts,
            status="failed",
            output=current_output,
            error=f"Repair failed after {self.policy.max_attempts} attempt(s).",
            validation_report=current_report,
        )
