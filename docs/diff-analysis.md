# GIR Diff Analysis

GIR diff analysis sits after Phase 7 change detection and classifies **what changed**, rather than only whether a node changed.

## Model

`GIRDiffAnalyzer.analyze(previous, current)` compares two maps of node IDs to `GIRNode` instances. Optional dependency maps can also be supplied when dependency relationships are part of the snapshot.

Each changed node produces a `GIRNodeDiff` containing:

- the node ID
- one or more deterministic semantic categories
- field-level differences
- previous/current GIR node types

Categories are:

- `STYLE` — theme, colors, typography, spacing and visual properties
- `LAYOUT` — layout, placement, sizing and component/section relationships
- `CONTENT` — headlines, subtitles, labels, copy and content assets
- `LOGIC` — actions, interactions, conditions and behavior
- `ARCHITECTURE` — frontend/backend/API/system and dependency relationships
- `STRUCTURAL` — added/removed nodes, type changes and structural relationships

A single node may have multiple categories. Results and field ordering are deterministic.

## Relationship to Phase 7

Phase 7 remains responsible for determining `ADDED`, `MODIFIED`, `UNCHANGED`, and `REMOVED` from persisted GIR fingerprints. Phase 8 consumes actual GIR snapshots to explain the semantics of a modification.

Diff analysis does **not** replace fingerprints, the `DependencyGraph`, cache, or `BuildPlanner`, and it does not decide generation behavior yet. It provides structured information that later build/generation strategies can use to avoid regenerating unrelated work.

## Current boundary

The classifier is rule-based and standard-library-only. Field names define the semantic mapping, so newly introduced GIR fields must be mapped explicitly. Unknown changed fields are conservatively classified as `STRUCTURAL` until their semantics are defined.
