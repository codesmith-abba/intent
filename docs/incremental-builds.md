# Incremental Builds

Incremental builds allow ITL to rebuild only the parts of a project whose effective input has changed, while preserving the existing source-cache and dependency-graph architecture.

The incremental build system is based on two distinct kinds of fingerprints:

- **Source fingerprints** describe the state of source files and remain the responsibility of the existing source cache.
- **GIR fingerprints** describe the semantic structure of generated intermediate representation nodes.

This separation is important. A source file can remain unchanged while the resulting GIR changes because of another input or transformation. Conversely, a source-level change may have no semantic effect on a particular GIR node. The two mechanisms therefore answer different questions and should not replace one another.

## Architecture

The incremental build flow is:

```text
Source files
    │
    ▼
Source cache ───────────────┐
    │                       │
    ▼                       │
GIR generation              │
    │                       │
    ▼                       │
GIR fingerprints            │
    │                       │
    ▼                       │
Change classification       │
    │                       │
    ▼                       │
Dependency invalidation     │
    │                       │
    ▼                       │
Build planner ◄─────────────┘
    │
    ▼
Build executor
    │
    ▼
Persist successful GIR state
```

The existing `DependencyGraph` remains the dependency source of truth. Incremental builds do not introduce a second dependency graph.

## GIR Fingerprints

`itl/gir/fingerprint.py` provides `GIRFingerprint.calculate(node)`.

A GIR node is canonicalized into a deterministic representation and hashed using SHA-256. Collection ordering is normalized where ordering is not semantically significant, making equivalent GIR structures produce the same fingerprint.

GIR fingerprinting is deliberately limited to GIR semantics. It does not replace source-file fingerprinting.

## Fingerprint State

`itl/gir/store.py` provides `GIRFingerprintStore` for persisting the last successful GIR state.

The state is stored as JSON at:

```text
.project/gir/fingerprints.json
```

`ProjectPaths.gir_fingerprints` is the canonical path used by the project infrastructure.

The store has the following guarantees:

- Missing state represents a project with no previous successful GIR build.
- State is validated when loaded and saved.
- JSON output is deterministic.
- Writes are atomic through a temporary file followed by `os.replace`.
- Corrupt state raises `IncrementalStateError` rather than silently discarding information.
- Fingerprint state is only replaced after a successful build.

## Change Classification

`itl/gir/changes.py` compares the previous persisted fingerprint map with the current map.

Every relevant node is classified as exactly one of:

| Change | Meaning |
| --- | --- |
| `ADDED` | The node exists now but did not exist in the previous state. |
| `MODIFIED` | The node existed previously, but its fingerprint changed. |
| `UNCHANGED` | The node exists in both states with the same fingerprint. |
| `REMOVED` | The node existed previously but no longer exists. |

Classification is deterministic: node identifiers are processed in sorted order.

The resulting change set is represented by `GIRChangeSet` and individual changes by `GIRNodeChange`.

## Dependency Invalidation

A GIR change does not necessarily mean that only the changed node must be rebuilt.

If another node depends on the changed node, that dependent may also need to be regenerated. ITL therefore uses the existing `DependencyGraph` to calculate affected nodes.

For an added or modified node:

```text
A changes
 │
 ├── B depends on A
 │    │
 │    └── C depends on B
 │
 └── D is independent
```

The affected set is:

```text
A, B, C
```

`D` remains unaffected.

The existing `DependencyGraph.affected_by()` method provides the transitive dependency behavior. `GIRDependencyInvalidator` is only an adapter around that existing graph; it does not maintain another graph.

### Removed Nodes

A removed node creates a special case because it may already have disappeared from the current graph. Its previous dependents therefore need to be available to the invalidation step when the graph has already been updated.

The incremental layer records removed nodes in the build plan rather than fabricating normal build items for nodes that no longer exist.

## Build Planning

`BuildPlanner` combines the existing source-cache decisions with GIR changes.

The responsibilities remain separate:

| Concern | Owner |
| --- | --- |
| Source-file fingerprinting | Existing source cache |
| Source cache hit/miss/invalidation | `CacheDecider` |
| GIR semantic fingerprinting | `GIRFingerprint` |
| GIR change classification | `GIRChangeDetector` |
| Dependency propagation | Existing `DependencyGraph` |
| Build scheduling | `BuildPlanner` |
| Build execution | `BuildExecutor` |
| Successful GIR state persistence | `GIRFingerprintStore` / build pipeline |

A GIR change can therefore cause a rebuild even when the source cache reports a hit. This is intentional: source caching and semantic GIR invalidation answer different questions.

The planner continues to use the graph's topological ordering for scheduled build items.

## Build Pipeline

`BuildPipeline` coordinates the incremental state around the existing build planner and executor.

Conceptually:

1. Load the last successful GIR fingerprint state.
2. Obtain the current GIR fingerprints.
3. Compare the two states.
4. Classify changes.
5. Propagate invalidation through the existing dependency graph.
6. Produce the normal build plan.
7. Execute the build.
8. Persist the new GIR fingerprint state only if execution succeeds.

This ordering prevents a failed build from being recorded as the new successful state.

## Build Behavior

### Initial build

When no fingerprint state exists, current GIR nodes are treated as newly added and are eligible for the initial build.

### Identical rebuild

If the current fingerprints are identical to the persisted fingerprints, nodes are `UNCHANGED`. GIR invalidation does not schedule additional work, and the existing source cache can continue to skip unchanged source files.

### Modified node

If a node's fingerprint changes, that node and its affected dependents are scheduled according to the dependency graph.

### Independent node

A node outside the dependency chain of the changed node is not rebuilt merely because another part of the project changed.

### Added node

A newly introduced node is classified as `ADDED` and its relevant dependents are considered by the invalidation system.

### Removed node

A previously persisted node that is no longer present is classified as `REMOVED`. It is exposed through the build plan so that the responsible output/backend layer can clean up artifacts associated with it.

## Failure and State Safety

Incremental state represents the last successful build, not merely the last attempted build.

For example:

```text
Successful build A
        │
        ▼
Persist fingerprints A
        │
        ▼
Build B starts
        │
        ├── execution succeeds ──► persist fingerprints B
        │
        └── execution fails ─────► retain fingerprints A
```

This prevents a failed build from poisoning future incremental decisions.

## Testing Expectations

The incremental build system should verify at least:

- deterministic GIR fingerprints
- persistence and reload of fingerprint state
- missing state handling
- malformed state handling
- all four change classifications
- deterministic classification order
- direct dependency invalidation
- transitive dependency invalidation
- independent-node isolation
- added nodes
- removed nodes
- unchanged builds
- GIR changes combined with source-cache hits
- dependency-aware build ordering
- failed builds preserving the previous fingerprint state

Tests use the repository's existing standard-library test style rather than introducing a separate test framework.

## Current Boundary

The incremental build layer is responsible for **detecting changes and planning work**. It is not an independent artifact-management system.

In particular, `BuildPlan.removed` identifies outputs that are no longer represented by the current GIR. The existing `BuildExecutor` does not itself delete generated artifacts. The backend/output layer that owns those artifacts is responsible for consuming the removal information and performing cleanup.

Keeping that responsibility outside the incremental planner avoids duplicating output-management architecture and keeps incremental builds focused on their core purpose: determining what has changed and what needs to be rebuilt.
