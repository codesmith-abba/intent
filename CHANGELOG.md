# Changelog

All notable ITL releases are documented here.

## [1.0.0] — 2026-09-12

### Stable

- Declared the first stable ITL release.
- Stabilized the implemented source-language boundary and versioned specification.
- Completed the pre-release conformance matrix across lexer, parser, AST, imports, semantic analysis, GIR, dependency graph, project state, cache, fingerprints, change detection, diff analysis, build planning, scheduling, AI generation, plugins, validation, repair, emission, CLI, browser runtime, security, package system, and local AI.
- Added deterministic incremental build and production-hardening coverage.
- Added installable Python package metadata and the `itl` console command.
- Packaged the browser runtime asset so installed `itl dev` does not depend on a repository checkout.
- Added v1.0 quickstart, architecture, language reference, plugin, release, and migration documentation.

### Compatibility policy

The stable source-language contract is the implemented behavior documented by `spec/ITL-0.1.md` and the release-facing reference in `docs/language-reference.md`.

The implementation version is `1.0.0`. Language-spec changes are versioned independently so compiler implementation improvements do not silently redefine source syntax.

## Pre-1.0 history

Earlier phase-specific behavior and implementation notes remain documented under `docs/phase-*` and the existing subsystem documentation.
