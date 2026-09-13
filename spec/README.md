# Intent Language Specification

This directory contains the **normative language specification** for Intent Language (ITL).

## Current specification

- [ITL Language Specification v0.3](ITL-0.3.md)
- [ITL Language Specification v0.2](ITL-0.2.md)
- [ITL Language Specification v0.1](ITL-0.1.md)
- [ITL v0.1 Specification Errata](ITL-0.1-ERRATA.md)

ITL v0.3 adds implemented authentication and authorization semantics, including authentication configuration, sessions, password recovery, verification, MFA, roles, inheritance, named permissions, and action/resource authorization while preserving the existing application-language semantics.

The specification is versioned independently from compiler implementation details. A specification version describes language behavior that is implemented and testable at the time it is published; it does not promise that every compiler or runtime implementation detail is stable.

## Separation of concerns

- `spec/` — normative language and semantic behavior.
- `docs/` — compiler, runtime, build, and implementation documentation.
- `ROADMAP.md` — future language and implementation work that is not part of the current specification.

Do not add proposed syntax to a released specification unless the implementation and conformance tests support it.
