# Emit System

Phase 14 adds the final filesystem boundary to the ITL build pipeline.

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
→ Repair
→ Validation
→ Emit
```

## Output mapping

`OutputMapper` converts a build-unit identifier into a relative target path. `RelativeOutputMapper` is the deterministic default and maps `.itl` / `.intent` sources to `.generated` outputs. Target/framework-specific integrations can provide their own mapper.

Absolute mapper results are rejected. Paths are resolved under the configured target root and paths containing `.git` or `.project` are rejected so generated content cannot overwrite repository or compiler state.

## Safe and atomic writes

Only `BuildResultStatus.SUCCESS` results are considered for emission. Failed generation, validation, and repair results are never written.

New and modified files are written to a temporary file in the destination directory, flushed and synced, then replaced with `os.replace`. A write failure therefore leaves the previous destination intact.

Identical content is reported as `UNCHANGED` without a write.

## Removed and stale outputs

The emitter keeps a small source-to-output manifest under `.project/emit/manifest.json`. This is compiler state, not generated project output.

`BuildPlan.removed` removes outputs for GIR nodes explicitly removed from the current project. Callers can also provide `current_sources`; entries in the manifest that are no longer represented are treated as stale and removed. Stale cleanup is only performed when the current source set is explicitly supplied.

## Dry run

`Emitter.emit(..., dry_run=True)` computes created, modified, unchanged, removed, and failed actions without modifying target files or the manifest. `BuildPipeline.build(..., dry_run=True)` forwards this mode and does not persist GIR fingerprints.

## Results

`EmitResults` records one `EmitResult` per attempted emission:

- `created`
- `modified`
- `unchanged`
- `removed`
- `failed`

`BuildOutcome.emission` exposes the emission results. Build state is persisted only when build validation and emission both succeed.

## Safety boundary

The emitter intentionally does not discover arbitrary files and does not emit compiler internals. It only writes successful textual build outputs through the configured mapper. Internal tracking remains under `.project`, while `.git` and `.project` are reserved from generated output.

## Testing

`tests/emit_test.py` covers creation, modification, unchanged output, removal, stale cleanup, failed generation/validation, atomic write failure, dry runs, path traversal, and reserved compiler-state protection. Tests use only the Python standard library and the repository's canonical `python -m tests` runner.
