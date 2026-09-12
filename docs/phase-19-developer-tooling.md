# ITL Phase 19 — Developer Tooling

Phase 19 adds compiler-backed editor tooling without creating a second ITL parser or semantic engine.

## Architecture

```text
Editor / IDE
    ↓ JSON-RPC / LSP adapter (optional protocol layer)
LSPServer
    ↓
EditorService
    ↓
Lexer → Parser → Analyzer
```

`EditorService` is the language-aware core. It consumes the existing lexer, parser, and semantic analyzer and adapts their results into editor concepts.

The LSP adapter in `itl/editor/server.py` uses only the Python standard library. No external LSP dependency is required by the compiler or editor core.

## Supported capabilities

- syntax diagnostics from the existing lexer/parser
- semantic diagnostics from the existing analyzer
- keyword and boolean completion
- keyword/symbol hover
- same-document definitions for application, page, and section symbols
- hierarchical document symbols
- conservative formatting (trailing whitespace and final newline only)
- JSON-RPC/LSP-style stdio transport

The current compiler does not expose source spans on every AST node, so navigation is deliberately limited to locations that can be derived safely from the current AST/source representation. Phase 19 does not invent a new source-location system.

## Running the language server

From the repository root:

```bash
python3 -m itl.editor.server
```

The process communicates over stdin/stdout using standard LSP-style `Content-Length` framed JSON-RPC messages.

There is intentionally no third-party package to install for the server.

## Programmatic API

```python
from itl.editor import EditorService, Position

service = EditorService()

source = "app $Store { target $web }"
diagnostics = service.diagnostics("app.itl", source)
completions = service.completions(source, Position(0, 25))
```

## Diagnostics

The editor layer does not recreate compiler validation. It invokes the actual:

1. `Lexer`
2. `Parser`
3. `Analyzer`

and converts their exceptions into editor diagnostics.

This keeps terminal/compiler behavior and editor diagnostics on the same implementation path.

## Formatting boundary

Formatting is intentionally conservative. It refuses to format invalid documents and only proposes whitespace-safe edits. It does not rewrite structural indentation or multiline intent content because those transformations would require stronger source-span information than the current compiler exposes.

## Tests

Phase 19 integration tests live in:

```text
tests/editor_test.py
```

Run the complete standard-library test suite:

```bash
python3 -m tests
```

The tests cover lexer/parser/analyzer diagnostics, completion, hover, symbols, definitions, formatting safety, and the LSP adapter.

## Future implementation boundary

A future editor phase may add an editor-specific source-span/index layer or a VS Code client. Such additions must continue to consume the compiler's lexical, parsing, and semantic services rather than introducing a parallel language implementation.
