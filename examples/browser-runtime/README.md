# ITL Browser Runtime Example

This example demonstrates the first usable browser runtime for ITL.

## Flow

```text
app.itl
   ↓
Lexer → Parser → Analyzer → GIR
   ↓
.project/runtime.json
   ↓
BrowserRuntime
   ↓
DOM + navigation + events + assets
```

The browser never parses `.itl` source. It consumes the generated runtime manifest produced from GIR.

## Run

From the repository root:

```bash
python3 -m itl build examples/browser-runtime
python3 -m http.server 8000
```

Open:

```text
http://localhost:8000/examples/browser-runtime/
```

The demo provides three pages, client-side navigation, a hero action, generated intent content, and a local SVG asset.

## Development mode

The existing `itl dev` command continues to provide a development build. The browser runtime itself is dependency-free JavaScript and can be used from any static development server.

## Runtime boundary

The compiler owns `.itl → GIR`.

The runtime owns:

- page resolution
- DOM rendering
- navigation
- browser events
- asset URL resolution
- runtime error reporting

No browser code imports parser, analyzer, or compiler internals.
