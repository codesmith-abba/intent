# Production Hardening

Phase 23 documents the operational guarantees of the current ITL implementation.

## Build behavior

- Build scheduling is deterministic: items are ordered by their position in the build plan.
- Dependency scheduling uses an indegree/reverse-edge traversal rather than repeatedly scanning the full remaining graph.
- A dependency cycle fails the build with a clear error instead of producing a partial schedule.
- Incremental GIR fingerprints are persisted atomically and only committed after build and emission succeed.
- A dry run does not persist GIR fingerprints.

## Crash recovery and persistence

- Cache JSON is written through a temporary file followed by `os.replace` and `fsync`.
- Generated GIR JSON artifacts use the same atomic-write pattern.
- Browser runtime manifests are also written atomically.
- If cache JSON is malformed or structurally invalid, ITL quarantines it as `entries.corrupt` and starts with an empty cache. The cache is disposable state, so this permits a clean rebuild instead of making the project unusable.
- GIR incremental state remains strict: invalid GIR fingerprint state raises `IncrementalStateError`, preventing ITL from silently accepting corrupted build decisions.

## Resumability

The build pipeline already accepts previous successful build results and persisted GIR fingerprints. A failed build therefore does not advance the persisted GIR state, and the next build can recompute the affected work. Successful work may be reused through the existing build result and cache abstractions.

## Observability

Build plans and summaries expose cache status, planned sources, success/failure/skipped counts, validation reports, and emission results. CLI errors wrap lower-level failures with the project and operation being performed.

The benchmark suite is intentionally measurement-first. Run:

```text
python benchmarks/production_bench.py
```

The benchmark reports lexer, 1,000-node scheduler, and 1,000-entry cache persistence timings. It is diagnostic rather than a pass/fail performance gate.

## Stress coverage

`tests/production_stress_test.py` covers a 5,000-node dependency chain, cache corruption recovery, and recovery followed by a successful cache write/read cycle.

## AI generation, validation, and repair

These subsystems retain their existing provider, validation, and repair boundaries. Production hardening does not couple the compiler to an AI provider. Generation failures remain errors at the generation boundary; build execution records failed items rather than silently treating them as successful.

## External execution

Phase 22 established secure-by-default subprocess behavior. Phase 23 does not loosen those capabilities. Dependency installation, lifecycle scripts, and development-server execution remain explicit capabilities.

## Performance principle

No speculative optimization is required. The scheduler was optimized because its previous implementation repeatedly scanned all remaining nodes for every batch, making long dependency chains unnecessarily expensive. The replacement performs a topological traversal over nodes and edges while preserving deterministic plan order.

## Recovery principle

Generated output and disposable cache state should never be left half-written. Persistent incremental state should fail closed when it cannot be trusted; disposable cache state should be quarantined and rebuilt automatically.
