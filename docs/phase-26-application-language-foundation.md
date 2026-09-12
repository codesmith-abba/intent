# Phase 26 — Application Language Foundation

Phase 26 moves ITL beyond UI/compiler infrastructure into application semantics.

## Implemented

- Model declarations and duplicate-model diagnostics.
- Field declarations and supported field types.
- Primary, required, unique, readonly, nullable, default, min/max, and minLen/maxLen constraints.
- Relationship declarations: `belongsTo`, `hasOne`, `hasMany`, `belongsToMany`, `hasManyThrough`.
- Application actions: `view`, `get`, `create`, `update`, `delete`, `manage`.
- Routes with path, page, and optional auth role.
- Permission roles, inheritance, and allow actions.
- Application-level `import $all` module resolution.
- AST and GIR representations for the new semantics.
- Semantic validation for duplicate declarations, invalid references, invalid types, invalid constraints, and invalid routes/roles.

## Golden example

`docs/examples/ecommerce/` remains the acceptance reference. Its existing `models.itl`, `routes.itl`, `permissions.itl`, pages, and `app.itl` are consumed without rewriting the example to fit the compiler.

The application continues to use:

```itl
import $all
```

for importing all project modules.

## Verification

Targeted Phase 26 tests are in `tests/phase26_application_language_test.py`. The full suite should be run before merging this phase.
