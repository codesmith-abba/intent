# ITL v1.0 Release Audit

This audit compares the actual repository implementation, Phase 24 conformance matrix, v0.1 language specification, and implementation roadmap before the v1.0 release gate.

## Language contract

| Area | v1.0 assessment | Evidence |
|---|---|---|
| Lexer | Stable/covered | Phase 18 + Phase 24 conformance tests |
| Parser | Stable/covered | Phase 18 + Phase 24 conformance tests |
| AST | Stable/covered | AST conformance and E2E tests |
| Imports | Stable/covered for implemented App→Page and Page→Section resolution | Spec §7 and import/E2E tests |
| Semantic analysis | Stable/covered | Semantic and validation tests |

The important release boundary is the implemented parser/analyzer language. Lexer-only reserved keywords remain unsupported source constructs.

## Compiler/build services

| Area | v1.0 assessment |
|---|---|
| GIR | Stable/covered |
| Dependency graph | Stable/covered |
| Project state | Stable/covered |
| Cache | Stable/covered, including corruption recovery |
| Fingerprints | Stable/covered |
| Change detection | Stable/covered |
| Diff analysis | Stable/covered |
| Build planning | Stable/covered |
| Scheduler | Stable/covered and deterministic |
| Incremental compilation | Stable/covered within implemented build pipeline |

These are implementation services rather than additional source-language syntax.

## AI, plugins, validation, and emit

| Area | v1.0 assessment |
|---|---|
| AI generation | Stable provider contract; no live external provider dependency |
| Local AI | Stable local provider contract; model server remains optional |
| Plugins | Stable extension boundary; trusted plugins are privileged code |
| Validation | Stable/covered |
| Repair | Stable/covered |
| Emit | Stable/covered |

No claim is made that AI-generated applications are universally correct or that plugins are sandboxed.

## CLI/runtime/package/security

| Area | v1.0 assessment |
|---|---|
| CLI | Stable command surface; installable `itl` entry point |
| Browser/runtime | Stable tested runtime manifest path; packaged runtime asset |
| Package system | Existing registry/security behavior covered; Python distribution packaging added for v1.0 |
| Security | Hardened defaults covered by Phase 22 tests; privileged trust boundaries remain explicit |
| Documentation | Release docs and subsystem docs present |
| Examples | Existing executable examples remain; release CI adds a clean-project smoke application |
| Test suite | Phase 24 matrix green before release work; Phase 25 adds packaging/release gates |

## Roadmap audit

The roadmap's pre-v1.0 implementation candidates fall into two groups:

### Implemented by v1.0

- package distribution tooling;
- plugin implementation and distribution boundaries;
- incremental build infrastructure;
- runtime manifest/browser runtime;
- validation/repair/emission pipeline;
- local AI runtime and security hardening.

### Intentionally still future

- first-class models/fields as source syntax;
- first-class routes/path declarations as source syntax;
- authentication/authorization source semantics;
- richer component declarations;
- explicit event/action semantics beyond current action content;
- formal source-level package/module declaration syntax;
- additional target-specific language semantics;
- additional backend implementations;
- structured diagnostic codes/severity;
- complete semantic validation of all infrastructure values.

These are not release blockers because the v1.0 contract does not claim they exist.

## Release-blocking findings fixed in Phase 25

1. **Python packaging was incomplete.** `pyproject.toml` was empty. It now declares the v1.0 distribution, Python requirement, console script, and package discovery.
2. **Installed browser development builds needed a repository checkout.** The browser runtime is now packaged under `itl.runtime` and `itl dev` resolves it through `importlib.resources`.
3. **Release documentation was stale.** The README, release docs, quickstart, language reference, plugin guide, architecture documentation, changelog, and migration notes now describe the stable release boundary.
4. **CI did not test installation from outside the checkout.** The release workflow now installs the package and runs `itl init`, `itl check`, and `itl build` from a temporary directory.

## Remaining release gate

The final v1.0.0 tag must wait for the Phase 25 CI workflow to pass after these changes. No later phase is part of this release.
