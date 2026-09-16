# Phase 27 — Authentication & Authorization Language

Phase 27 makes authentication and authorization first-class ITL application semantics.

## Authentication

Implemented AST, parser, semantic analysis, and GIR support for:

- `auth`
- authentication providers
- registration
- login
- logout
- password recovery/reset
- verification
- sessions and duration values
- remember-me
- multi-device sessions
- MFA configuration

Providers remain user-defined. The compiler does not hard-code ecommerce authentication providers.

## Authorization

Implemented general-purpose authorization constructs for:

- roles
- role inheritance
- named permissions
- resource permissions
- action permissions
- direct `allow` action/resource rules

The common action vocabulary is `view`, `get`, `create`, `update`, `delete`, and `manage`.

The ecommerce roles `guest`, `customer`, `seller`, `admin`, and `superAdmin` are example declarations, not compiler built-ins.

## Semantic validation

Phase 27 validates:

- duplicate roles
- unknown inherited roles
- circular inheritance
- duplicate permissions
- unknown permission resources
- invalid permission actions
- unknown role permission references
- duplicate authentication providers
- unknown authentication provider references
- invalid session durations
- enabled MFA without a method
- protected routes referencing unknown roles

## GIR

Authentication configuration and authorization semantics are represented explicitly in GIR so backend generators can consume them without depending on the source parser.

## Golden example

`docs/examples/ecommerce/auth.itl` and `permissions.itl` are consumed using the existing syntax. The application continues to use `import $all`.

## Verification boundary

Phase 27 is complete only after the targeted Phase 27 tests and the full repository suite pass. Phase 28 is intentionally not part of this phase.
