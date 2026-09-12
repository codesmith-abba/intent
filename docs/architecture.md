# ITL v1.0 Architecture

ITL v1.0 is organized around a stable language boundary and replaceable implementation services.

```text
.itl source
   |
   v
Lexer -> Parser -> AST -> Import Resolution -> Semantic Analysis
                                             |
                                             v
                                            GIR
                                             |
             +-------------------------------+------------------------------+
             |               |               |              |                |
          Graph           Diff/          Planner/        Generation       Runtime
                         Fingerprint      Scheduler       /Plugins
             |               |               |              |                |
             +---------------+---------------+--------------+----------------+
                                             |
                                      Validation/Repair
                                             |
                                           Emit
```

## Language boundary

The normative source language is defined by the implemented lexer, parser, resolver, and analyzer. The current reference is `spec/ITL-0.1.md`.

The parser intentionally accepts a smaller language than the full set of lexer tokens. Lexically reserved but unsupported constructs are not v1.0 source features.

## GIR

GIR is the compiler's intermediate boundary between source-language semantics and downstream build/runtime services. It carries application, page, component, system, intent, and target information needed by those services.

## Incremental build

GIR fingerprints and diffs classify changes. The dependency graph identifies affected work. The build planner produces dependency-safe work and the scheduler preserves deterministic ordering. Cache state allows unchanged work to be reused where the corresponding build integration supports it.

## AI generation

AI is an optional implementation capability. Generation is isolated behind provider contracts and is validated before emission. The local provider supports OpenAI-compatible local HTTP endpoints; no live external AI service is required for the test suite.

## Plugins

Plugins extend generation and validation through the existing plugin manager. They are implementation extensions and do not introduce new ITL source syntax.

Security controls treat plugins and package installation as explicit trust boundaries. Trusted Python plugins and explicitly enabled package lifecycle scripts are privileged capabilities rather than sandbox guarantees.

## Browser runtime

The browser runtime consumes generated runtime manifests. It does not parse `.itl` source. The packaged distribution includes the browser runtime asset so `itl dev` works after installation without requiring a repository checkout.

## CLI

The `itl` executable is the supported command-line entry point. It delegates to project services for initialization, checking, building, development output, graph inspection, planning, explanation, and cleaning.

## Determinism and recovery

The compiler/build layers favor deterministic ordering, deterministic fingerprints, atomic persistence, and explicit failure/recovery behavior. Cache corruption is quarantined rather than treated as valid state.
