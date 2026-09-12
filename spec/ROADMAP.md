# ITL Language and Implementation Roadmap

This document is **non-normative**. Items here are proposals or future implementation work and are not part of ITL Language Specification v0.1 unless they are explicitly implemented and added to a later specification version.

## Language evolution candidates

- First-class model declarations and field constraints.
- First-class route/path declarations.
- Authentication, roles, permissions, and authorization semantics.
- A formal module/import naming convention and package model.
- Richer component composition and reusable component declarations.
- Explicit event/action semantics.
- Formal asset declarations.
- Additional target-specific semantics.
- A stable version declaration in source projects, if required by future compatibility work.

## Compiler implementation candidates

- More precise source locations on all tokens and diagnostics.
- Structured diagnostic codes and severity levels.
- More complete semantic validation for database, cache, storage, API, and infrastructure values.
- Stronger incremental invalidation rules across imported modules.
- Additional backend implementations.
- More complete runtime manifest semantics.
- Package and plugin distribution tooling.

## Specification process

For each future language release:

1. Inspect the actual lexer/parser/analyzer behavior.
2. Decide the intended language change.
3. Implement the language change.
4. Add conformance tests.
5. Update the versioned specification.
6. Update implementation documentation separately.
7. Record future or rejected syntax here rather than presenting it as current syntax.
