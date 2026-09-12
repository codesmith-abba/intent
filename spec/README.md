# Intent Language Specification

This directory contains the **normative language specification** for Intent Language (ITL).

## Current specification

- [ITL Language Specification v0.1](ITL-0.1.md)
- [ITL v0.1 Specification Errata](ITL-0.1-ERRATA.md)

The specification is versioned independently from compiler implementation details. A specification version describes language behavior that is implemented and testable at the time it is published; it does not promise that every compiler or runtime implementation detail is stable.

The errata file is normative for v0.1 and overrides conflicting wording discovered during conformance testing.

## Separation of concerns

- `spec/` — normative language and semantic behavior.
- `docs/` — compiler, runtime, build, and implementation documentation.
- `ROADMAP.md` — future language and implementation work that is not part of the current specification.

Do not add proposed syntax to a released specification unless the implementation and conformance tests support it.
