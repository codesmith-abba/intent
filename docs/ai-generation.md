# Phase 10 — AI Generation

Phase 10 adds AI as a replaceable generation backend behind the existing build system.

## Pipeline position

```text
.ITL source
  -> Lexer
  -> Parser
  -> AST
  -> Semantic Analysis
  -> GIR
  -> Dependency Graph
  -> Change Detection
  -> Diff Analysis
  -> Build Plan
  -> Scheduler
  -> AI Generation
  -> Validation
  -> Emit
```

Generation does not parse ITL source and is not involved in lexing, parsing, or semantic analysis.

## Generation units

`AIGenerator` receives the existing `BuildItem` selected by `BuildPlanner` and `BuildScheduler`. A caller supplies a `GenerationContext` for each scheduled unit. Context can be constructed directly from a normalized `GIRNode` with `GenerationContext.from_gir()`.

The context contains:

- unit identity and normalized GIR type
- intent
- constraints
- dependency identities
- target and framework
- relevant existing output
- optional normalized metadata

This keeps raw `.itl` text out of the generation boundary.

## Provider abstraction

Providers implement the small `GenerationProvider` protocol:

```python
response = provider.generate(request, prompt)
```

The compiler core does not select or hard-code an AI vendor or model. Provider responses contain generated output plus provider/model metadata.

## Prompt construction

`GenerationPromptBuilder` produces deterministic prompts with explicit sections for:

- requested unit
- unit type
- target
- framework
- intent
- constraints
- dependencies
- existing relevant output

The same normalized request produces the same prompt.

## Cache and incremental generation

`AIGenerator` can use the existing `Cache`. A valid cached generated output is returned without a provider call. Cache writes use the existing cache persistence path.

Incremental behavior remains owned by the existing compiler pipeline:

1. GIR changes identify affected nodes.
2. `BuildPlanner` creates only affected build items.
3. `BuildScheduler` orders those items by dependency.
4. `BuildExecutor` invokes `AIGenerator.build()` only for scheduled items.

Phase 10 therefore does not introduce a second build pipeline or regenerate the whole project.

## Failure behavior

Provider exceptions become `GenerationResult(status=FAILED, error=...)`. When used through `AIGenerator.build()`, the structured result is wrapped in `GenerationFailure`, which the existing `BuildExecutor` records as a normal build failure. Failed generation therefore does not update successful project/GIR state.

## Testing

Tests use a standard-library fake provider. No external AI API is required. The suite covers context construction, deterministic prompts, success, provider failure, cache hits, incremental scheduling, and scheduler-to-provider dependency ordering.

No threading or processes are introduced in Phase 10. The Phase 9 scheduler remains the future parallelism boundary.
