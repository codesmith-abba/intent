# ITL CLI

Phase 15 makes the CLI a thin interface over the existing project/compiler services.

## Entry point

```bash
python -m itl <command> <project>
```

The `itl` command discovers the nearest project by looking for `.project` and
uses `app.itl` as the project entrypoint.

## Commands

### `itl init <project>`

Creates the standard `.project` state directories and `state.json` using the
existing `ProjectInitializer`.

### `itl check <project>`

Compiles the project through the existing project `Compiler` without writing
generated output. Compilation errors are reported as CLI errors and return a
non-zero exit code.

### `itl explain <project>`

Uses the existing `Pipeline` and `Explainer` to provide the project's current
human-readable explanation.

### `itl build <project>`

Compiles the project through the existing pipeline, writes the existing IR
artifacts under the discovered project's `.project` directory, and records the
entrypoint in the existing cache. The output includes cache status/reason so
incremental decisions are visible to the user.

Use `--dry-run` to compile and report the planned build/cache action without
writing build output or cache state.

### `itl plan <project>`

Reports the current cache decision for the project entrypoint without building.

### `itl graph <project>`

Displays persisted graph information when available. The CLI does not create a
second dependency-graph implementation.

### `itl dev <project>`

Runs the existing React backend generation path into `.project/build`.
This command reports completion; it does not claim to launch a long-running
watch server because no watcher/server service exists in the current compiler.

### `itl clean <project>`

Removes `.project/build`, leaving compiler state and source files intact.

## Exit codes

- `0` — command succeeded.
- `1` — project/compiler/build failure.
- `2` — CLI usage/argument failure.
- `130` — interrupted by the user.

## Architecture rule

CLI parsing and output formatting stay in `itl/cli.py`. Project discovery,
compiler invocation, cache handling, and filesystem lifecycle operations live in
`itl/cli_service.py` or the existing compiler/project modules. Compiler logic
is not embedded in command handlers.

## Testing

`tests/cli_test.py` exercises the CLI through subprocesses, including project
initialization, valid/invalid projects, missing projects, build and dry-run,
explain, clean, graph/plan output, and exit-code/error behavior.
