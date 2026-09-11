# Build Scheduler

Phase 9 adds dependency-aware scheduling on top of the existing `BuildPlan`, `DependencyGraph`, incremental planning, and executor.

## API

`BuildScheduler.schedule(plan, completed=None)` returns a `BuildSchedule` containing ordered `BuildBatch` objects. Each batch contains work whose dependencies are already resolved, so the items in one batch can later be executed concurrently without changing scheduling semantics.

Example:

```text
A       C
|       |
B       D
 \     /
   E
```

produces conceptually:

```text
Batch 1: A, C
Batch 2: B, D
Batch 3: E
```

Ordering within a batch is deterministic (sorted source IDs).

## Failure handling

`BuildExecutor` now consumes scheduler batches. If a dependency failed or was skipped, its dependent item is recorded as `SKIPPED` and its builder is not called. This prevents invalid downstream execution while allowing independent work to continue.

## Resume

`BuildExecutor.execute(..., previous_results=...)` accepts successful previous results. Successful work is treated as already completed and is not rebuilt; dependents can proceed from that completed state. Failed work is not treated as completed.

`BuildPipeline.build(..., previous_results=...)` exposes the same resume capability without replacing the existing planner or executor architecture.

## Cycles

The scheduler rejects a cyclic `BuildPlan` with `ValueError`. The existing `DependencyGraph` also rejects cycles when dependencies are added and continues to provide canonical graph-level validation.

## Boundaries

Phase 9 does not add threads, processes, or AI generation. Batches establish the execution boundary for future parallelism while keeping current execution sequential and deterministic.
