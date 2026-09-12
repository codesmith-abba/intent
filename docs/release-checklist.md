# ITL v1.0.0 Release Checklist

## Repository

- [x] Version is `1.0.0`.
- [x] Package metadata exists in `pyproject.toml`.
- [x] `itl` console entry point is declared.
- [x] Browser runtime asset is packaged.
- [x] Apache-2.0 license remains present.

## Language

- [x] Lexer behavior covered.
- [x] Parser behavior covered.
- [x] AST and imports covered.
- [x] Semantic rules covered.
- [x] Normative language specification reviewed against implementation.
- [x] Lexer-only/reserved syntax is explicitly excluded from the stable language contract.

## Compiler/build

- [x] GIR covered.
- [x] Dependency graph covered.
- [x] Fingerprints covered.
- [x] Change/diff analysis covered.
- [x] Incremental planning covered.
- [x] Scheduler determinism covered.
- [x] Cache persistence/recovery covered.

## AI/plugins

- [x] AI generation contracts covered.
- [x] Local AI provider covered.
- [x] Plugin architecture and trust boundary documented/tested.
- [x] Validation and repair covered.
- [x] Emission covered.

## CLI/runtime

- [x] CLI command behavior covered.
- [x] Project initialization/lifecycle covered.
- [x] Browser runtime tests pass.
- [x] Installed `itl` command is smoke-tested outside the repository checkout.
- [x] Installed `itl dev` can access the packaged browser runtime asset.

## Documentation

- [x] Changelog.
- [x] Migration notes.
- [x] Release notes.
- [x] Quickstart.
- [x] Language reference.
- [x] Plugin guide.
- [x] Architecture documentation.
- [x] Test/conformance matrix.

## Verification gate

- [x] Phase 24 CI suite green before release work.
- [ ] Phase 25 CI suite green after all release changes.
- [ ] Clean checkout/package installation smoke test green.
- [ ] End-to-end `.itl` build smoke test green.
- [ ] Release tag `v1.0.0` created only after the final CI gate is green.

## Release rule

Do not publish or tag v1.0.0 until every unchecked verification item above is green. No Phase 26 work is part of the v1.0 release milestone.
