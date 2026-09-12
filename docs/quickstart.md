# ITL v1.0 Quickstart

## 1. Install

ITL v1.0.0 requires Python 3.10 or newer.

From a checkout:

```bash
python -m pip install .
```

Verify the installation:

```bash
itl --help
python -c "import itl; print(itl.__version__)"
```

## 2. Create a project

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

## 3. Validate

```bash
itl check hello-itl
```

## 4. Build GIR/output

```bash
itl build hello-itl
```

The generated compiler state is written under `hello-itl/.project/`.

## 5. Generate the development browser build

```bash
itl dev hello-itl
```

The browser development output is under:

```text
hello-itl/.project/build/browser/
```

It contains the runtime bundle, runtime manifest, and an `index.html` entry point.

## 6. Inspect the project

```bash
itl explain hello-itl
itl graph hello-itl
itl plan hello-itl
```

## 7. Clean generated development output

```bash
itl clean hello-itl
```

## Scope of v1.0

The v1.0 language is the syntax accepted by the lexer, parser, import resolver, and semantic analyzer and documented in `spec/ITL-0.1.md`. Build, GIR, incremental compilation, plugins, AI generation, validation, repair, emission, package, security, and browser-runtime behavior are implementation services around that language boundary.
