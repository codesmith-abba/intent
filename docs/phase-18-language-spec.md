# Phase 18 — Formal Language Specification

Phase 18 establishes the first versioned ITL language specification without changing the language implementation.

## Source-of-truth inspection

The specification was derived from the implemented:

- `itl/parser/lexer.py`
- `itl/parser/token_type.py`
- `itl/parser/parser.py`
- `itl/parser/ast.py`
- `itl/compiler/compiler.py`
- `itl/compiler/resolver.py`
- `itl/analyzer/analyzer.py`
- `itl/analyzer/constants.py`
- `itl/gir/models.py`
- `itl/gir/builder.py`

The important distinction is that the lexer recognizes more tokens than the parser currently accepts. Phase 18 therefore documents **implemented parser behavior**, not every token that happens to exist in the lexer.

## Language vs implementation

### Normative language

`spec/ITL-0.1.md` defines:

- lexical behavior;
- supported source grammar;
- names and string literals;
- blocks and imports;
- pages and components;
- targets and frameworks;
- semantic validation;
- GIR meaning at the language boundary;
- language-level error categories.

### Compiler implementation

The compiler currently loads `app.itl`, resolves supported imports, runs semantic analysis, and builds GIR. The import resolver currently supports these merges:

```text
App  <- Page
Page <- Section
```

This is implementation behavior and is described separately from source syntax.

### Build/runtime implementation

The repository also contains build, generation, validation, repair, emission, plugin, and browser-runtime systems. These consume GIR or build artifacts and are intentionally not presented as new language syntax in v0.1.

## Versioning policy

The current version is **v0.1**. A future language change should:

1. change the implementation;
2. add or update conformance tests;
3. update the versioned specification;
4. document compiler/runtime consequences separately;
5. record proposals in `spec/ROADMAP.md` until implemented.

## Verification

Run the full suite:

```bash
python3 -m tests
```

The Phase 18 conformance module is:

```bash
python3 -m tests.phase18_conformance_test
```

No Phase 19 work is included in this phase.
