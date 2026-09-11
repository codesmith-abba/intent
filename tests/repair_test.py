from dataclasses import dataclass

from itl.build.executor import BuildExecutor
from itl.build.models import BuildItem, BuildPlan
from itl.build.results import BuildResultStatus
from itl.cache.decision import CacheStatus
from itl.generation.models import GenerationContext
from itl.repair.models import RepairPolicy
from itl.repair.provider import RepairProviderResponse
from itl.repair.repairer import AIRepairer
from itl.validation.models import (
    ValidationContext,
    ValidationIssue,
    ValidationResult,
    ValidationStatus,
)
from itl.validation.pipeline import ValidatorPipeline


@dataclass
class RuleValidator:
    name: str = "rule"

    def validate(self, context: ValidationContext) -> ValidationResult:
        if context.output == "valid":
            return ValidationResult(
                unit_id=context.unit_id,
                validator=self.name,
                status=ValidationStatus.PASSED,
            )
        return ValidationResult(
            unit_id=context.unit_id,
            validator=self.name,
            status=ValidationStatus.FAILED,
            issues=(
                ValidationIssue(
                    validator=self.name,
                    message="Output must be valid.",
                    code="invalid_output",
                ),
            ),
        )


@dataclass
class SequenceProvider:
    outputs: list[str]
    calls: int = 0

    def repair(self, request, prompt):
        output = self.outputs[min(self.calls, len(self.outputs) - 1)]
        self.calls += 1
        return RepairProviderResponse(
            output=output,
            provider="test",
            model="repair-test",
        )


@dataclass
class RaisingProvider:
    calls: int = 0

    def repair(self, request, prompt):
        self.calls += 1
        raise RuntimeError("provider unavailable")


def context(unit: str = "home"):
    return {
        unit: GenerationContext(
            unit_id=unit,
            unit_type="page",
            target="web",
            framework="react",
        )
    }


def failed_report(unit: str = "home"):
    return ValidatorPipeline([RuleValidator()]).validate(
        ValidationContext(unit_id=unit, output="invalid", source=unit)
    )


def repairer(provider, max_attempts=3):
    return AIRepairer(
        provider=provider,
        contexts=context(),
        validator=ValidatorPipeline([RuleValidator()]),
        policy=RepairPolicy(max_attempts=max_attempts),
    )


def item():
    return BuildItem(source="home", status=CacheStatus.MISS, dependencies=set())


def test_successful_repair():
    provider = SequenceProvider(["valid"])
    result = repairer(provider).repair(item(), "invalid", failed_report())

    assert result.succeeded
    assert result.output == "valid"
    assert result.attempt == 1
    assert result.validation_report is not None
    assert result.validation_report.passed
    assert provider.calls == 1


def test_failed_repair_after_max_retries():
    provider = SequenceProvider(["still-invalid"])
    result = repairer(provider, max_attempts=2).repair(item(), "invalid", failed_report())

    assert not result.succeeded
    assert result.attempt == 2
    assert result.validation_report is not None
    assert not result.validation_report.passed
    assert provider.calls == 2


def test_validation_runs_after_every_repair():
    provider = SequenceProvider(["still-invalid", "valid"])
    result = repairer(provider, max_attempts=2).repair(item(), "invalid", failed_report())

    assert result.succeeded
    assert result.attempt == 2
    assert provider.calls == 2


def test_provider_failure_is_structured():
    provider = RaisingProvider()
    result = repairer(provider).repair(item(), "invalid", failed_report())

    assert not result.succeeded
    assert result.error == "provider unavailable"
    assert result.attempt == 1
    assert provider.calls == 1


def test_unchanged_valid_output_is_preserved():
    report = ValidatorPipeline([RuleValidator()]).validate(
        ValidationContext(unit_id="home", output="valid", source="home")
    )
    provider = SequenceProvider(["unused"])
    result = repairer(provider).repair(item(), "valid", report)

    assert result.succeeded
    assert result.output == "valid"
    assert result.attempt == 0
    assert result.metadata["unchanged"] is True
    assert provider.calls == 0


def test_unchanged_repair_output_is_final_failure():
    provider = SequenceProvider(["invalid"])
    result = repairer(provider).repair(item(), "invalid", failed_report())

    assert not result.succeeded
    assert result.error == "Repair provider returned unchanged output."
    assert provider.calls == 1


def test_multiple_validation_failures_are_carried_into_repair_context():
    class MultiValidator:
        name = "multi"

        def validate(self, validation_context):
            if validation_context.output == "valid":
                return ValidationResult(
                    unit_id=validation_context.unit_id,
                    validator=self.name,
                    status=ValidationStatus.PASSED,
                )
            return ValidationResult(
                unit_id=validation_context.unit_id,
                validator=self.name,
                status=ValidationStatus.FAILED,
                issues=(
                    ValidationIssue("multi", "first failure", code="first"),
                    ValidationIssue("multi", "second failure", code="second"),
                ),
            )

    provider = SequenceProvider(["valid"])
    repair = AIRepairer(
        provider=provider,
        contexts=context(),
        validator=ValidatorPipeline([MultiValidator()]),
    )
    initial_report = ValidatorPipeline([MultiValidator()]).validate(
        ValidationContext(unit_id="home", output="invalid", source="home")
    )
    assert len(initial_report.issues) == 2
    result = repair.repair(item(), "invalid", initial_report)

    assert result.succeeded
    assert result.attempt == 1
    assert provider.calls == 1


def test_build_executor_accepts_repaired_output_as_success():
    provider = SequenceProvider(["valid"])
    repair = repairer(provider)
    executor = BuildExecutor(
        builder=lambda build_item: "invalid",
        validator=ValidatorPipeline([RuleValidator()]),
        repairer=repair,
    )
    results = executor.execute(BuildPlan(items=[item()]))

    assert results.results[-1].status == BuildResultStatus.SUCCESS
    assert results.results[-1].output == "valid"
    assert results.results[-1].validation_report is not None
    assert results.results[-1].validation_report.passed
