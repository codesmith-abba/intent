# ITL Storefront — Phase 16 End-to-End Example

This example is a small multi-page storefront compiled with the existing ITL compiler and incremental build services.

## Why multiple `.itl` files?

The current language/compiler treats an `app` declaration as a compilation unit. It does not yet define a separate multi-file application-composition/import pipeline. Phase 16 therefore deliberately uses one small application unit per page so the existing compiler can build a realistic dependency graph without inventing a new language feature.

The units together represent one storefront:

```text
shell → home → catalog → product → checkout
```

Each unit contains real ITL application/page/component intent and targets the already-supported `web` + `react` combination.

## Build workflow demonstrated by the Phase 16 test

1. Read `.itl` source.
2. Lex and parse it into AST.
3. Run semantic analysis.
4. Build GIR.
5. Fingerprint the GIR.
6. Build the dependency graph.
7. Detect GIR changes.
8. Classify semantic diffs.
9. Produce a dependency-safe build plan.
10. Schedule independent work in batches.
11. Generate React output through the existing reference plugin.
12. Validate generated output through the plugin validation boundary.
13. Repair invalid output when a repair provider is configured.
14. Emit only validated output with the existing safe emitter.

The test intentionally exercises the same project repeatedly to demonstrate why incremental compilation matters.

## Change scenarios

The end-to-end test covers:

- initial build
- unchanged second build
- content change
- style/theme change
- structural section change
- dependency graph change
- validation failure
- repair
- successful rebuild
- emitted output

Run the full suite with:

```bash
python3 -m tests
```
