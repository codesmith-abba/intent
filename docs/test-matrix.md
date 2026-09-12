# ITL v1.0 Test & Conformance Matrix

Phase 24 defines the pre-v1.0 verification matrix for the implemented ITL compiler, build system, AI pipeline, runtime, CLI, package system, and security boundaries.

The matrix was created from the existing `tests/` suite before adding new coverage. Existing tests remain in place; Phase 24 adds focused language-conformance coverage rather than replacing working tests.

## Test policy

- Python tests use the repository's standard-library test runner (`python -m tests`).
- Tests are deterministic and must not require live network services unless a test explicitly targets an external boundary through a fake/local fixture.
- Existing integration and end-to-end tests remain authoritative for cross-component behavior.
- Invalid input, failure, recovery, determinism, and incremental behavior are treated as first-class cases.
- A passing matrix means the implemented behavior is exercised; it does not claim unsupported features exist.

## Matrix

| # | Area | Existing / Phase 24 tests | Unit | Integration | E2E | Invalid / failure | Recovery | Determinism | Incremental | Status |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| 1 | Lexer | `phase18_conformance_test.py`, `phase24_conformance_test.py` | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | Covered |
| 2 | Parser | `phase18_conformance_test.py`, `phase24_conformance_test.py` | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | Covered |
| 3 | AST | `phase18_conformance_test.py`, `phase24_conformance_test.py`, `phase16_e2e_test.py` | ✓ | ✓ | ✓ | ✓ | — | — | — | Covered |
| 4 | Imports | `phase18_conformance_test.py`, `phase24_conformance_test.py`, `phase16_e2e_test.py` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | Covered |
| 5 | Semantic analysis | `phase18_conformance_test.py`, `validation_test.py`, `project_validator_test.py` | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | Covered |
| 6 | GIR | `gir_diff_test.py`, `gir_fingerprint_test.py`, `gir_incremental_test.py`, `phase16_e2e_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 7 | Dependency graph | `graph_test.py`, `build_planner_test.py`, `build_scheduler_test.py`, `phase16_e2e_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 8 | Project state | `project_state_test.py`, `project_state_store_test.py`, `project_lifecycle_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 9 | Cache | `cache_test.py`, `cache_decider_test.py`, `cache_invalidation_test.py`, `cache_persistence_test.py`, `cache_store_test.py`, `cache_store_persistence_test.py`, `cache_validator_test.py`, `production_stress_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 10 | Fingerprints | `fingerprint_test.py`, `gir_fingerprint_test.py` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | Covered |
| 11 | Change detection | `cache_decider_test.py`, `cache_invalidation_test.py`, `gir_diff_test.py`, `gir_incremental_test.py`, `build_pipeline_incremental_test.py`, `phase16_e2e_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 12 | Diff analysis | `gir_diff_test.py`, `phase16_e2e_test.py` | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | Covered |
| 13 | Build planning | `build_plan_test.py`, `build_planner_test.py`, `build_pipeline_test.py`, `build_integration_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 14 | Scheduler | `build_scheduler_test.py`, `production_stress_test.py`, `generation_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 15 | AI generation | `generation_test.py`, `phase16_e2e_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 16 | Plugins | `plugin_system_test.py`, `phase16_e2e_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 17 | Validation | `validation_test.py`, `project_validator_test.py`, `phase16_e2e_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 18 | Repair | `repair_test.py`, `phase16_e2e_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 19 | Emit | `emit_test.py`, `phase16_e2e_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 20 | CLI | `cli_test.py`, `project_manager_test.py`, `project_initializer_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 21 | Runtime | `browser_runtime_manifest_test.py`, `browser_runtime_test.js`, `phase16_e2e_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 22 | Security | `security_test.py`, `plugin_system_test.py`, `local_provider_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Covered |
| 23 | Package system | `package_registry_test.py`, `plugin_system_test.py`, `security_test.py` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | Covered |
| 24 | Local AI | `local_provider_test.py`, `generation_test.py` | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | Covered |

## Cross-cutting conformance classes

### Unit tests

Focused component behavior is covered across lexer/parser, compiler analysis, GIR, graph/build primitives, cache/state, generation, validation, repair, emission, plugins, CLI, security, package, and local-AI modules.

### Integration tests

The build pipeline, cache decisions, scheduler, validation/repair, plugin generation, and runtime manifest are exercised through component combinations. `phase16_e2e_test.py` provides the primary multi-stage integration boundary.

### End-to-end tests

`phase16_e2e_test.py` exercises a real storefront fixture through compilation, graph construction, incremental builds, diff classification, generation, validation, repair, and emission. Browser runtime behavior is separately exercised by `browser_runtime_test.js`.

### Regression tests

Phase-specific tests remain in the suite (`phase16_e2e_test.py`, `phase18_conformance_test.py`, `production_stress_test.py`) so previously implemented behavior stays executable. The test runner discovers every `*_test.py` module deterministically.

### Invalid input and failure tests

The suite covers lexical errors, parser errors, semantic errors, invalid cache state, generation-provider failure, validation failure, repair paths, scheduler dependency-cycle failures, plugin trust/integrity failures, package validation failures, CLI failures, and local-AI transport/configuration failures.

### Failure recovery

Production-hardening recovery behavior is exercised by cache corruption/quarantine tests and project-state persistence tests. Build execution and repair tests also verify that failed intermediate stages do not silently become successful output.

### Determinism

Determinism is explicitly exercised for lexer output, generation prompts, fingerprints, diff/build decisions, scheduler ordering, cache persistence, and the production stress scheduler. The repository's test runner also sorts test modules and test functions.

### Incremental builds

Incremental behavior is covered by cache invalidation, GIR fingerprint/incremental tests, build-pipeline incremental tests, generation scheduling, and the Phase 16 storefront E2E workflow. The E2E workflow verifies unchanged units are skipped and affected units are rebuilt after content, style, structural, and dependency changes.

## Coverage gaps and deliberate non-goals

The matrix is a behavioral/conformance matrix, not a claim of mathematical or exhaustive input-space coverage. The following remain known gaps or deliberate non-goals for v1.0:

1. **No property-based or fuzzing framework** is introduced; the project remains standard-library-first.
2. **No external-provider live tests** are required for AI generation. Provider contracts are tested with fakes; local AI is tested with local HTTP fixtures/configuration rather than a required installed model server.
3. **No benchmark pass/fail thresholds** are asserted. Phase 23 benchmarks remain diagnostic because premature performance thresholds would be arbitrary without representative production workloads.
4. **No OS matrix beyond the CI environment** is claimed. Filesystem behavior is tested through temporary directories, while CI currently runs on Ubuntu.
5. **No security sandbox guarantee** is claimed for trusted Python plugins or explicitly enabled install scripts; Phase 22 documents these as privileged capabilities.
6. **No generated-code semantic equivalence proof** is claimed. Validation and repair verify the implemented validation contracts, not arbitrary correctness of AI-generated applications.
7. **No public v1.0 compatibility guarantee for undocumented syntax** is inferred from tests. Conformance follows actual implemented lexer/parser/analyzer behavior.

## CI execution

The authoritative Python suite is:

```text
python -m tests
```

The browser runtime suite is:

```text
node tests/browser_runtime_test.js
```

Both are already part of `.github/workflows/tests.yml`.

## Phase 24 completion rule

Phase 24 is complete only when the full CI suite is green after the matrix and focused conformance tests are committed. Phase 25 is intentionally not included in this phase.
