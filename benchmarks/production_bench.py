"""Small stdlib-only production benchmarks.

Run with: python benchmarks/production_bench.py
The numbers are informational; no performance threshold is assumed here.
"""

from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from itl.build.models import BuildItem, BuildPlan
from itl.build.scheduler import BuildScheduler
from itl.cache.cache import Cache
from itl.parser.lexer import Lexer
from itl.parser.source import SourceFile


def measure(label, operation, iterations=10):
    started = perf_counter()
    for _ in range(iterations):
        operation()
    elapsed = perf_counter() - started
    print(f"{label}: {elapsed / iterations * 1000:.3f} ms/op ({iterations} iterations)")


def main():
    source_text = "\n".join(["intent home", "    title $Home", "    description $Production benchmark"])
    source = SourceFile(path=Path("benchmark.itl"), text=source_text)
    measure("lexer", lambda: Lexer(source).scan_tokens(), iterations=1000)

    items = [BuildItem(source=f"page-{index}", status=None) for index in range(1000)]
    for index in range(1, len(items)):
        items[index].dependencies.add(items[index - 1].source)
    plan = BuildPlan(items=items)
    scheduler = BuildScheduler()
    measure("scheduler-1000-chain", lambda: scheduler.schedule(plan), iterations=20)

    with TemporaryDirectory() as directory:
        cache = Cache(directory)
        for index in range(1000):
            source_path = Path(directory) / f"source-{index}.itl"
            source_path.write_text("intent page", encoding="utf-8")
            cache.put(source_path)
        measure("cache-save-1000", cache.save, iterations=5)


if __name__ == "__main__":
    main()
