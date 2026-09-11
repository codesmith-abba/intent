# Phase 12 — Validation System

Validation is the gate between generation and accepting generated output as a successful build artifact.

## Position in the pipeline

```text
.ITL source
→ Lexer
→ Parser
→ AST
→ Semantic Analysis
→ GIR
→ Dependency Graph
→ Change Detection
→ Diff Analysis
→ Build Plan
→ Scheduler
→ AI Generation
→ Validation
→ Emit
```

Validation does not replace generation, the build scheduler, or plugin infrastructure. It consumes generated output through a small, composable validator contract.

## Core model

`ValidationContext` identifies the build unit and carries its generated output plus optional target, framework, and metadata.

`Validator` is the stable protocol:

```python
class Validator(Protocol):
    @property
    def name(self) -> str: ...

    def validate(self, context: ValidationContext) -> ValidationResult: ...
```

`ValidationResult` records the unit, validator, status, and structured issues. `ValidationReport` aggregates all validator results for one unit. `ValidationSummary` aggregates reports across a build.

Statuses are `PASSED`, `FAILED`, and `SKIPPED`.

## Validator pipeline

`ValidatorPipeline` accepts any number of validators and runs them in registration order. Validators are independent and composable. A validator exception is converted into a structured failed result rather than escaping as an unclassified failure.

A validator must return a result for the same unit and with its own declared name. Invalid validator results are treated as validation failures.

## Build integration

`BuildExecutor` accepts an optional `ValidatorPipeline`. When present, generation completes first and the generated output is immediately validated before a successful `BuildResult` is recorded.

A validation failure produces:

- the build unit/source
- `BuildResultStatus.FAILED`
- the generated output for diagnostics
- a `ValidationFailure` exception
- the complete `ValidationReport`

Therefore invalid generated output cannot be treated as successful build output and cannot satisfy dependent build units as a successful dependency.

`BuildResult.validation_report` exposes the per-unit report. `BuildOutcome.validation` derives the aggregate validation summary from its build results.

## Plugin validation

Phase 11 already defined plugin validation hooks. `PluginValidator` adapts `PluginManager.validate()` to the core `Validator` interface. This keeps framework-specific validation inside plugins while the compiler core remains framework-independent.

A plugin with no validation capability returns `SKIPPED`, not a false success or failure.

## Future validator categories

The architecture supports adding validators for:

- generated syntax/output
- formatting
- compiler/build checks
- tests
- linting
- accessibility
- plugin-specific rules
- architecture and contract rules

Phase 12 does not require concrete implementations for every category. Those validators can be introduced independently without changing the core pipeline contract.

## Failure behavior

Validator failures are blocking. Validator exceptions are also blocking and are reported with an `validator_exception` issue code. This makes validation deterministic and prevents an unavailable or broken validator from silently approving generated output.

## Testing

The standard-library test suite covers passing and failing validators, multiple validators, validator exceptions, aggregation, build failure integration, successful validation, and plugin validation integration.
