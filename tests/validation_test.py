from itl.build.executor import BuildExecutor
from itl.build.models import BuildItem, BuildPlan
from itl.cache.decision import CacheStatus
from itl.plugins import PluginManager, PluginRegistry
from itl.plugins.reference_react import ReactReferencePlugin
from itl.generation.models import GenerationContext, GenerationRequest
from itl.validation import (
    PluginValidator,
    ValidationContext,
    ValidationIssue,
    ValidationResult,
    ValidationStatus,
    ValidatorPipeline,
)


class PassingValidator:
    name = "passing"

    def validate(self, context):
        return ValidationResult(
            unit_id=context.unit_id,
            validator=self.name,
            status=ValidationStatus.PASSED,
        )


class FailingValidator:
    name = "failing"

    def validate(self, context):
        return ValidationResult(
            unit_id=context.unit_id,
            validator=self.name,
            status=ValidationStatus.FAILED,
            issues=(ValidationIssue(self.name, "invalid output", code="invalid"),),
        )


class RaisingValidator:
    name = "raising"

    def validate(self, context):
        raise RuntimeError("validator exploded")


def _context(output="output"):
    return ValidationContext(unit_id="home", source="home.itl", output=output)


def _plan():
    return BuildPlan(
        items=[
            BuildItem(source="home", status=CacheStatus.MISS),
        ]
    )


def test_passing_validator():
    report = ValidatorPipeline((PassingValidator(),)).validate(_context())
    assert report.passed
    assert report.results[0].status == ValidationStatus.PASSED


def test_failing_validator_aggregates_structured_issue():
    report = ValidatorPipeline((FailingValidator(),)).validate(_context())
    assert not report.passed
    assert report.issues[0].code == "invalid"
    assert report.issues[0].validator == "failing"


def test_multiple_validators_are_composable():
    report = ValidatorPipeline((PassingValidator(), FailingValidator())).validate(_context())
    assert report.validators_run == 2
    assert len(report.failed) == 1


def test_validator_exception_becomes_failure():
    report = ValidatorPipeline((RaisingValidator(),)).validate(_context())
    assert not report.passed
    assert report.issues[0].code == "validator_exception"
    assert report.issues[0].details == (("exception", "RuntimeError"),)


def test_build_failure_integration():
    executor = BuildExecutor(
        builder=lambda item: "bad output",
        validator=ValidatorPipeline((FailingValidator(),)),
    )
    results = executor.execute(_plan())
    result = results.results[0]
    assert result.status.value == "failed"
    assert result.validation_report is not None
    assert not results.succeeded


def test_build_success_requires_validation_to_pass():
    executor = BuildExecutor(
        builder=lambda item: "valid output",
        validator=ValidatorPipeline((PassingValidator(),)),
    )
    results = executor.execute(_plan())
    result = results.results[0]
    assert result.status.value == "success"
    assert result.validation_report is not None


def test_validation_exception_prevents_success():
    executor = BuildExecutor(
        builder=lambda item: "output",
        validator=ValidatorPipeline((RaisingValidator(),)),
    )
    result = executor.execute(_plan()).results[0]
    assert result.status.value == "failed"
    assert result.validation_report is not None
    assert result.validation_report.issues[0].code == "validator_exception"


def test_plugin_validator_passes_reference_plugin_output():
    registry = PluginRegistry()
    registry.register(ReactReferencePlugin())
    manager = PluginManager(registry)

    validator = PluginValidator(
        manager,
        lambda context: GenerationRequest(
            context=GenerationContext(
                unit_id=context.unit_id,
                unit_type="GIRPage",
                target="web",
                framework="react",
            ),
            requested_unit=context.unit_id,
        ),
    )
    report = ValidatorPipeline((validator,)).validate(
        _context("export default function Home() { return <div />; }")
    )
    assert report.passed


def test_plugin_validator_fails_invalid_reference_output():
    registry = PluginRegistry()
    registry.register(ReactReferencePlugin())
    manager = PluginManager(registry)
    validator = PluginValidator(
        manager,
        lambda context: GenerationRequest(
            context=GenerationContext(
                unit_id=context.unit_id,
                unit_type="GIRPage",
                target="web",
                framework="react",
            ),
            requested_unit=context.unit_id,
        ),
    )
    result = validator.validate(_context("const broken = true;"))
    assert result.failed
    assert result.issues[0].code == "plugin_validation_error"


def test_build_outcome_exposes_validation_summary():
    from itl.build.outcome import BuildOutcome
    from itl.build.summary import summarize

    executor = BuildExecutor(
        builder=lambda item: "bad",
        validator=ValidatorPipeline((FailingValidator(),)),
    )
    results = executor.execute(_plan())
    outcome = BuildOutcome(
        plan=_plan(),
        results=results,
        summary=summarize(results, total_sources=1),
    )
    assert outcome.validation is not None
    assert not outcome.validation.passed
