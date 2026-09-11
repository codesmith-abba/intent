# Testing

ITL uses a dependency-free development test harness built on Python's standard library. The language itself does not require a third-party package for its test infrastructure.

## Test Model

The repository's tests are ordinary Python modules containing zero-argument functions whose names begin with `test_`.

Example:

```python
def test_example():
    result = some_operation()
    assert result == expected
```

Tests remain executable individually as Python modules:

```bash
python3 -m tests.build_executor_test
```

## Complete Test Suite

The `tests` package provides its own module entry point:

```bash
python3 -m tests
```

`tests/__main__.py` discovers every module matching `*_test.py`, imports it, discovers every zero-argument `test_*` function, and executes the functions in deterministic order.

The runner exits with status `0` when all tests pass and status `1` when any test fails or a test module cannot be imported.

This deliberately avoids introducing pytest or another external testing dependency.

## Automatic CI Testing

GitHub Actions runs the same command on every push and pull request:

```bash
python -m tests
```

The CI environment installs only the Python interpreter needed to execute the repository's development test suite. It does not install project-specific third-party test packages.

This keeps local and CI execution aligned:

```text
Developer machine
      │
      ▼
python3 -m tests
      │
      ▼
ITL test runner
      │
      ├── compiler tests
      ├── parser tests
      ├── GIR tests
      ├── graph tests
      ├── cache tests
      ├── build tests
      └── integration tests

GitHub Actions runs the same command
```

## Why This Fits ITL

The test infrastructure is a development concern, not a runtime dependency of the ITL language.

ITL can therefore remain dependency-free for its own implementation goals while the repository still has:

- deterministic test discovery
- explicit assertions
- individual test execution
- complete-suite execution
- CI verification
- non-zero failure status for automation

As the compiler evolves, tests should increasingly include actual `.itl` programs and end-to-end compiler behavior, rather than only testing internal Python implementation details.
