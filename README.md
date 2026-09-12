# Intent Language (ITL)

> **Programming by intention, not implementation.**

Intent Language (ITL) is an open-source declarative programming language and compiler for describing application intent and transforming it into a structured intermediate representation and generated runtime artifacts.

**v1.0.0 — Stable**

## What is stable in v1.0

ITL v1.0.0 stabilizes the implemented language/compiler boundary and the surrounding build tooling:

- lexer and parser
- AST and import resolution
- semantic analysis
- Graph Intermediate Representation (GIR)
- dependency graph and build planning
- deterministic scheduling
- fingerprints, diff analysis, and incremental builds
- cache persistence and recovery
- AI generation contracts
- plugin architecture
- validation, repair, and emission
- project lifecycle and CLI
- browser runtime and runtime manifests
- package-system boundaries
- security hardening
- local AI provider

The release does **not** claim that every lexer token is a supported language construct, that every possible backend is implemented, or that AI-generated output is automatically correct. Unsupported and future capabilities remain outside the v1.0 language contract.

## Install

ITL requires Python 3.10 or newer.

From a source checkout:

```bash
python -m pip install .
```

Verify:

```bash
itl --help
python -c "import itl; print(itl.__version__)"
```

## Quickstart

Create a project:

```bash
mkdir hello-itl
itl init hello-itl
```

Create `hello-itl/app.itl`:

```itl
app $Hello {
    page $home {
        hero $main {
            headline $Hello from ITL
            subtitle $Programming by intention.
            action $Explore
        }
    }
    target $web
}
```

Validate and build:

```bash
itl check hello-itl
itl build hello-itl
```

Generate the browser development build:

```bash
itl dev hello-itl
```

Inspect a project:

```bash
itl explain hello-itl
itl graph hello-itl
itl plan hello-itl
```

See [`docs/quickstart.md`](docs/quickstart.md) for the complete walkthrough.

## Language reference

The normative source-language specification is [`spec/ITL-0.1.md`](spec/ITL-0.1.md). It is intentionally derived from the implemented lexer, parser, resolver, and semantic analyzer.

The release-facing reference is [`docs/language-reference.md`](docs/language-reference.md).

Important: the lexer reserves more words than the parser currently accepts. Lexical recognition does not make a keyword a supported language feature.

## Compiler architecture

```text
.itl source
    |
    v
  Lexer
    |
    v
  Parser
    |
    v
   AST
    |
    v
Import Resolution
    |
    v
Semantic Analysis
    |
    v
   GIR
    |
    +-------------------+
    |                   |
Dependency Graph    Build Planning
    |                   |
    +--------+----------+
             |
        Scheduler
             |
     Generation/Plugins
             |
       Validation
             |
          Repair
             |
           Emit
             |
      Runtime Artifacts
```

GIR is the boundary between source-language semantics and downstream build/runtime services. Incremental compilation uses fingerprints, change/diff analysis, dependency impact, planning, scheduling, and cache state.

See [`docs/architecture.md`](docs/architecture.md).

## CLI

The supported executable is `itl`.

| Command | Purpose |
|---|---|
| `itl init <project>` | Initialize an ITL project |
| `itl check <project>` | Validate and compile the project |
| `itl build <project>` | Build compiler/GIR output |
| `itl dev <project>` | Generate development/browser output |
| `itl explain <project>` | Explain compiled intent |
| `itl graph <project>` | Inspect persisted dependency graph |
| `itl plan <project>` | Inspect cache/build decision |
| `itl clean <project>` | Remove development build output |

## Browser runtime

`itl dev` produces a browser development bundle containing:

- `browser.js`
- `runtime.json`
- `index.html`

The browser runtime consumes the generated runtime manifest; it does not parse `.itl` source. The runtime asset is included in the installed Python package.

## AI and local AI

AI is an optional implementation capability, not a requirement for the language. Generation is isolated behind provider contracts and validated before emission.

The local provider supports OpenAI-compatible local HTTP endpoints. See [`docs/local-ai.md`](docs/local-ai.md).

## Plugins

Plugins extend generation and validation through the existing implementation-level plugin system. They do not introduce new `.itl` syntax.

Trusted Python plugins are privileged code; v1.0 does not claim a security sandbox for them. See [`docs/plugins.md`](docs/plugins.md).

## Security

ITL v1.0 applies secure defaults around subprocess execution, package installation, plugins, local AI endpoints, secrets, cache persistence, and project paths. Privileged capabilities remain explicit trust boundaries.

See the existing security and production-hardening documentation under `docs/`.

## Testing

The project uses Python's standard-library test runner. No pytest dependency is required.

```bash
python -m tests
node tests/browser_runtime_test.js
```

The CI workflow also installs the package, verifies the version, runs the installed CLI outside the checkout, performs a clean project build, and runs the complete test suite.

See [`docs/test-matrix.md`](docs/test-matrix.md).

## Project structure

```text
intent/
├── itl/                 # compiler, language, build, runtime, CLI
├── runtime/             # repository browser-runtime fixture
├── examples/            # executable example projects
├── spec/                # normative language specification
├── docs/                # subsystem and release documentation
├── tests/               # standard-library test suite
├── benchmarks/          # diagnostic production benchmarks
├── pyproject.toml       # v1.0 package metadata
├── CHANGELOG.md
└── LICENSE
```

## Versioning

ITL uses semantic implementation releases beginning at `1.0.0`.

The implementation/distribution version and language-specification version are tracked separately. A compiler implementation patch must not silently change the accepted language. A language change requires updated implementation behavior, conformance tests, and a new versioned specification.

## Release documentation

- [`CHANGELOG.md`](CHANGELOG.md)
- [`docs/release-1.0.0.md`](docs/release-1.0.0.md)
- [`docs/release-checklist.md`](docs/release-checklist.md)
- [`docs/migration-1.0.md`](docs/migration-1.0.md)
- [`docs/quickstart.md`](docs/quickstart.md)
- [`docs/language-reference.md`](docs/language-reference.md)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/plugins.md`](docs/plugins.md)

## License

Apache License 2.0. See [`LICENSE`](LICENSE).

## Project status

ITL v1.0.0 is the first stable release. Future language changes should be proposed and versioned rather than introduced silently.
