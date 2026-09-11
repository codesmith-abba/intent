# ITL Phase 17 — Browser Runtime

Phase 17 introduces the first usable browser runtime without adding a second compiler pipeline.

## Architecture

```text
.itl
  ↓
Lexer → Parser → Analyzer → GIR
  ↓
IRWriter / BrowserManifestBuilder
  ↓
.project/runtime.json
  ↓
BrowserRuntime (runtime/browser.js)
  ↓
DOM
```

The browser runtime does not parse ITL and does not import compiler internals. The Python adapter converts the existing GIR into a small stable runtime manifest.

## Runtime representation

The manifest is versioned (`0.1`) and contains application metadata, the initial page, and serialized GIR pages/components. This keeps the browser boundary independent from Python dataclasses.

## Rendering

The first renderer supports the existing GIR component types:

- pages
- heroes
- sections
- nested sections
- intent text
- themes as page metadata

The renderer uses normal browser DOM APIs and no frontend framework.

## Navigation

Pages are addressable through URL hashes. The runtime supports:

- initial-page resolution
- navigation links
- `history.pushState`
- browser back/forward state
- hash changes
- hero actions that resolve to a page name

## Events/actions

The runtime uses delegated click handling for navigation. Actions that do not resolve to a page are emitted as runtime `action` events, allowing future application services to subscribe without changing the renderer.

## Assets

`AssetManager` resolves relative assets against a configured asset root and passes absolute/data/blob URLs through unchanged. Image load failures are reported through the runtime error channel.

## Development mode

`itl dev <project>` now produces both the existing development output and a browser bundle under:

```text
.project/build/browser/
├── browser.js
├── runtime.json
└── index.html
```

The bundle can be served by any static development server.

## Error reporting

Runtime failures are represented as `ITLRuntimeError` and shown in the configured runtime root. The runtime also logs the normalized error to the browser console.

## Compiler/runtime integration

`IRWriter` writes `runtime.json` whenever a GIR application is emitted. The browser therefore consumes generated representation rather than `.itl` source.

The runtime is deliberately small. It does not own compilation, semantic analysis, scheduling, generation, validation, or emission.

## Example

See `examples/browser-runtime/` for a three-page storefront with navigation, a hero action, intent content, and an SVG asset.

Run:

```bash
python3 -m itl build examples/browser-runtime
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/examples/browser-runtime/
```

## Tests

Python integration tests verify GIR → runtime manifest generation and real compiler output. Node tests exercise browser runtime startup, rendering, navigation, unknown-page errors, and asset resolution.
