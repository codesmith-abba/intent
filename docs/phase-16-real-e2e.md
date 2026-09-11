# Phase 16 — Real End-to-End Application

Phase 16 proves the existing ITL compiler/build infrastructure against a realistic multi-page storefront example without introducing a new compiler architecture.

## Example

`examples/storefront/` contains five compilation units:

- `shell.itl` — shared storefront shell/navigation intent
- `home.itl` — landing page
- `catalog.itl` — catalog/filtering experience
- `product.itl` — product details and delivery information
- `checkout.itl` — order completion flow

The dependency graph is:

```text
shell
  ↓
home
  ↓
catalog
  ↓
product
  ↓
checkout
```

The current language does not yet define a separate multi-file application-composition/import build pipeline, so the example intentionally keeps one `app` declaration per compilation unit. This demonstrates real incremental dependency behavior without inventing a new language feature.

## End-to-end path

For every build unit the test starts with the actual compiler:

```text
.itl
  ↓
Lexer
  ↓
Parser
  ↓
AST
  ↓
Semantic Analysis
  ↓
GIR
```

The resulting GIR is fingerprinted and passed into the existing incremental build system:

```text
GIR
  ↓
Dependency Graph
  ↓
Change Detection
  ↓
Diff Analysis
  ↓
Build Plan
  ↓
Scheduler
  ↓
Generation
  ↓
Validation
  ↓
Repair (when configured)
  ↓
Emit
```

Generation uses the repository's supported `web` + `react` reference plugin. No external AI service is required.

## Incremental scenarios

The end-to-end test intentionally performs successive builds.

### 1. Initial build

All five units are compiled, scheduled, generated, validated, and emitted.

Five `.generated` files are produced in the emitter output directory.

### 2. Unchanged build

The same GIR fingerprints are supplied again. The persisted fingerprint state and source cache allow the planner to avoid processing all five units.

### 3. Content change

The home-page hero headline changes. GIR diff analysis identifies the hero field as `CONTENT`. The home page and its downstream dependents are scheduled.

### 4. Style change

The catalog theme changes from `light` to `dark`. The GIR `theme` field is classified as `STYLE`. The catalog and downstream dependents are affected.

### 5. Structural change

A new reviews section is inserted into the product page. The page's component structure changes and is classified as `STRUCTURAL`.

### 6. Dependency change

Checkout receives an additional dependency on the shared shell. The dependency snapshot changes and GIR diff analysis classifies it as `ARCHITECTURE` + `STRUCTURAL`.

### 7. Validation failure

A deliberately invalid generated React output is passed through the normal validation pipeline. The reference plugin rejects it.

### 8. Repair

A deterministic reference repair provider is configured through the existing `AIRepairer` boundary. The repaired candidate is validated again.

### 9. Successful rebuild

The repaired output becomes the successful build result.

### 10. Emit

The existing `Emitter` writes only validated output and uses its normal safe-path and atomic-write behavior.

## Test

Run the complete suite:

```bash
python3 -m tests
```

The focused Phase 16 test is:

```bash
python3 -m tests.phase16_e2e_test
```

The test is intentionally integration-heavy. It verifies the behavior of the already-existing compiler/build services together rather than introducing a parallel test-only compiler implementation.

## What this proves

Phase 16 demonstrates that ITL is not only a parser/compiler experiment. A meaningful application can be expressed as ITL intent, transformed into GIR, tracked incrementally, generated for a supported framework, validated, repaired when necessary, and safely emitted.

The example also makes the value of incremental compilation observable: a small source/GIR change does not require every unrelated unit to be regenerated.
