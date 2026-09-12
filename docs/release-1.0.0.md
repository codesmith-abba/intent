# ITL v1.0.0 Release

**Release:** 1.0.0  
**Date:** 2026-09-12  
**Status:** Stable

## What v1.0 means

ITL v1.0.0 is the first stable implementation release. The stable contract is the implemented language behavior documented in `spec/ITL-0.1.md`, together with the compiler/build/runtime services covered by the Phase 24 conformance matrix.

This release does not claim that every lexer token is a supported language construct, that every backend is production-ready, or that AI-generated output is automatically correct. Unsupported and future capabilities remain outside the v1.0 contract.

## Stable areas

The release audit covers:

- lexer and parser behavior;
- AST and imports;
- semantic analysis;
- GIR generation;
- dependency graph and build planning;
- fingerprints, diff analysis, and incremental behavior;
- deterministic scheduling and cache recovery;
- AI generation contracts and local AI provider;
- plugin architecture;
- validation, repair, and emission;
- CLI/project lifecycle;
- browser runtime and runtime manifests;
- package registry/system boundaries;
- security hardening;
- documentation and conformance tests.

## Installation

```bash
python -m pip install .
```

Verify:

```bash
itl --help
python -c "import itl; print(itl.__version__)"
```

## Quickstart

See `docs/quickstart.md`.

## Specification

The normative language specification remains `spec/ITL-0.1.md`. The release-facing guide is `docs/language-reference.md`.

## Architecture

See `docs/architecture.md` for the stable compiler/build/runtime architecture and boundaries.

## Plugins

See `docs/plugins.md` for compatibility, trust, generation, and validation guidance.

## Verification

The release gate requires:

```bash
python -m tests
node tests/browser_runtime_test.js
python -m pip install .
itl --help
```

CI also verifies the package installation path and clean-environment CLI smoke test.

## Known boundaries

The v1.0 release intentionally does not add major new language features. Known non-goals and coverage gaps are recorded in `docs/test-matrix.md`.
