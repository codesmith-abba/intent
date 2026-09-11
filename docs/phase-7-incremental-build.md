# Phase 7 — Incremental Builds

Phase 7 adds deterministic GIR-based change tracking without replacing the existing source cache or dependency graph.

## 7.1 — GIR fingerprints

`itl/gir/fingerprint.py` provides `GIRFingerprint.calculate(node)` and produces a deterministic SHA-256 fingerprint from the semantic GIR structure. This phase does not modify that implementation.

## 7.2 — Fingerprint persistence

`itl/gir/store.py` provides `GIRFingerprintStore`.

- State is stored as JSON.
- Missing state is treated as an initial build (`{}`).
- State is validated when loaded and saved.
- Writes use a temporary file followed by `os.replace`, preventing partial final files.
- `ProjectPaths.gir_fingerprints` is the canonical project location: `.project/gir/fingerprints.json`.

Corrupt state raises `IncrementalStateError` instead of silently discarding previous build information.

## 7.3 — Change classification

`itl/gir/changes.py` compares previous and current fingerprint maps and classifies every node as:

- `ADDED`
- `MODIFIED`
- `UNCHANGED`
- `REMOVED`

Classification is deterministic because node IDs are processed in sorted order.

## 7.4 — Dependency-aware invalidation

`itl/gir/invalidation.py` uses the existing `DependencyGraph`; it does not introduce a second graph implementation.

An added or modified node invalidates itself and all transitive dependents through `DependencyGraph.affected_by()`.

A removed node is no longer present in the current graph, so its previously-known dependents can be supplied through `previous_dependents` when the graph has already been updated.

## 7.5 — Build planner integration

`BuildPlanner.plan()` now accepts an optional `GIRChangeSet`. GIR invalidation is additive to the existing source-cache behavior:

- `SourceFingerprint` / `CacheDecider` remains responsible for source-file cache decisions.
- `GIRFingerprint` remains responsible for semantic GIR change detection.
- A GIR change can therefore schedule a rebuild even when the source cache reports a hit.
- Removed GIR nodes are represented on `BuildPlan.removed` rather than being fabricated as build items.

Existing dependency ordering remains controlled by `DependencyGraph.topological_order()`.

## 7.6 — Pipeline persistence

`BuildPipeline` optionally accepts a `GIRFingerprintStore` and current GIR fingerprints. It loads the previous state before planning, computes changes, executes the existing plan, and persists the new state only when execution succeeds.

This gives the following behavior:

1. First build: no fingerprint state exists, so current nodes are `ADDED` and are scheduled.
2. Second identical build: nodes are `UNCHANGED`; no GIR-driven rebuild is scheduled.
3. A modified node: that node and its transitive dependents are scheduled.
4. An independent node remains untouched.
5. Removed nodes are reported in the build plan for output/state cleanup by the owning build/output layer.
6. A failed build does not overwrite the last successful GIR fingerprint state.

## Current Phase 7 limitation

The incremental layer tracks and plans removed nodes, but `BuildExecutor` does not itself delete generated artifacts. The owning output/backend layer must consume `BuildPlan.removed` to perform artifact cleanup. This phase deliberately avoids inventing a parallel artifact-deletion system.
