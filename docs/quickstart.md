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

From inside the project, the project argument can be omitted:

```bash
cd hello-itl
itl check
```

## 4. Build GIR/output

```bash
itl build
```

The generated compiler state is written under `.project/`.

## 5. Generate and start the development server

```bash
itl dev
```

`itl dev` builds the development output and starts the React/Vite development server automatically. On the default Vite port, open:

```text
http://localhost:5173
```

The development output is under:

```text
.project/build/
```

It contains the React application and browser runtime output.

The first `itl dev` automatically installs the generated npm dependencies when they are not already installed. Installation uses `--ignore-scripts` by default for safety. Use `--allow-install-scripts` only when lifecycle scripts are explicitly trusted.

To generate the development build without starting the server:

```bash
itl dev --no-run
```

The explicit form remains supported:

```bash
itl dev --run
```

## 6. Inspect the project

```bash
itl explain
itl graph
itl plan
```

## 7. Clean generated development output

```bash
itl clean
```

## Scope of v1.0

The v1.0 language is the syntax accepted by the lexer, parser, import resolver, and semantic analyzer and documented in `spec/ITL-0.1.md`. Build, GIR, incremental compilation, plugins, AI generation, validation, repair, emission, package, security, and browser-runtime behavior are implementation services around that language boundary.
