"""Run the complete ITL test suite with the Python standard library only."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import sys
import traceback
from pathlib import Path


PACKAGE_NAME = __package__ or "tests"
TEST_SUFFIX = "_test"
TESTS_DIR = Path(__file__).resolve().parent


def discover_test_modules() -> list[str]:
    """Return test modules in deterministic order."""
    modules = [
        module.name
        for module in pkgutil.iter_modules([str(TESTS_DIR)])
        if module.name.endswith(TEST_SUFFIX)
    ]
    return sorted(modules)


def discover_test_functions(module: object) -> list[str]:
    """Return zero-argument test functions in deterministic order."""
    functions = []

    for name, value in inspect.getmembers(module, inspect.isfunction):
        if not name.startswith("test_"):
            continue

        signature = inspect.signature(value)
        if signature.parameters:
            raise TypeError(
                f"Test function {module.__name__}.{name} must not require arguments"
            )

        functions.append(name)

    return sorted(functions)


def run() -> int:
    """Discover and execute every ITL test function."""
    print("Running ITL test suite...\n")

    passed = 0
    failed = 0
    modules = discover_test_modules()

    if not modules:
        print("No test modules found.")
        return 1

    for module_name in modules:
        qualified_name = f"{PACKAGE_NAME}.{module_name}"

        try:
            module = importlib.import_module(qualified_name)
            test_functions = discover_test_functions(module)
        except Exception:
            failed += 1
            print(f"✗ {qualified_name} (module discovery/import failed)")
            traceback.print_exc()
            continue

        module_passed = 0
        module_failed = 0

        for function_name in test_functions:
            test_name = f"{qualified_name}.{function_name}"
            function = getattr(module, function_name)

            try:
                function()
            except Exception:
                failed += 1
                module_failed += 1
                print(f"✗ {test_name}")
                traceback.print_exc()
            else:
                passed += 1
                module_passed += 1
                print(f"✓ {test_name}")

        if module_failed == 0:
            print(f"  {module_passed} test(s) passed\n")
        else:
            print(f"  {module_passed} passed, {module_failed} failed\n")

    print("=" * 60)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")

    if failed:
        print("ITL test suite failed.")
        return 1

    print("All ITL tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
