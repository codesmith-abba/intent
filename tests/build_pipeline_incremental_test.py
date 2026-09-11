from pathlib import Path
from tempfile import TemporaryDirectory

from itl.build.executor import BuildExecutor
from itl.build.pipeline import BuildPipeline
from itl.build.planner import BuildPlanner
from itl.cache.cache import Cache
from itl.cache.decider import CacheDecider
from itl.graph.graph import DependencyGraph
from itl.gir.store import GIRFingerprintStore


def test_identical_gir_build_skips_after_state_is_persisted():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "home.itl"
        source.write_text("home", encoding="utf-8")

        cache = Cache(root)
        graph = DependencyGraph()
        graph.add_node(str(source))
        planner = BuildPlanner(CacheDecider(cache), graph)
        calls = []
        executor = BuildExecutor(lambda item: calls.append(item.source))
        store = GIRFingerprintStore(root / ".project" / "gir" / "fingerprints.json")
        pipeline = BuildPipeline(planner, executor, store)

        first = pipeline.build([source], {str(source): "one"})
        second = pipeline.build([source], {str(source): "one"})

        assert first.plan.sources == [str(source)]
        assert second.plan.sources == []
        assert calls == [str(source)]
        assert store.load() == {str(source): "one"}


def test_modified_gir_node_rebuilds_its_dependents_even_on_source_cache_hit():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        a = root / "a.itl"
        b = root / "b.itl"
        a.write_text("a", encoding="utf-8")
        b.write_text("b", encoding="utf-8")

        cache = Cache(root)
        cache.put(str(a))
        cache.put(str(b))
        cache.save()

        graph = DependencyGraph()
        graph.add_dependency(str(b), str(a))
        planner = BuildPlanner(CacheDecider(cache), graph)
        executor = BuildExecutor(lambda item: item.source)
        store = GIRFingerprintStore(root / ".project" / "gir" / "fingerprints.json")
        store.save({str(a): "old", str(b): "same"})
        pipeline = BuildPipeline(planner, executor, store)

        outcome = pipeline.build(
            [a, b],
            {str(a): "new", str(b): "same"},
        )

        assert outcome.plan.sources == [str(a), str(b)]
        assert store.load() == {str(a): "new", str(b): "same"}


if __name__ == "__main__":
    test_identical_gir_build_skips_after_state_is_persisted()
    test_modified_gir_node_rebuilds_its_dependents_even_on_source_cache_hit()
    print("All incremental build pipeline tests passed.")
