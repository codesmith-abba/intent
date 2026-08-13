from pathlib import Path
from tempfile import TemporaryDirectory

from itl.build.executor import BuildExecutor
from itl.build.pipeline import BuildPipeline
from itl.build.planner import BuildPlanner
from itl.cache.cache import Cache
from itl.cache.decider import CacheDecider
from itl.graph.graph import DependencyGraph


def test_pipeline_builds_plan_and_executes():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        home = root / "home.itl"

        home.write_text(
            "page $home {}",
            encoding="utf-8",
        )

        cache = Cache(root)

        graph = DependencyGraph()

        graph.add_node(str(home))

        executed = []

        def builder(item):

            executed.append(
                item.source
            )

            cache.put(
                item.source,
                output=f"generated:{item.source}",
            )

        planner = BuildPlanner(
            CacheDecider(cache),
            graph,
        )

        executor = BuildExecutor(
            builder
        )

        pipeline = BuildPipeline(
            planner,
            executor,
        )

        outcome = pipeline.build(
            [home]
        )

        plan = outcome.plan
        results = outcome.results
        summary = outcome.summary
        assert plan.sources == [
            str(home)
        ]

        assert executed == [
            str(home)
        ]

        assert results.succeeded

        assert len(
            results.successful
        ) == 1

        assert (
            results.successful[0].source
            == str(home)
        )

        assert summary.processed == 1
        assert summary.successful == 1
        assert summary.failed == 0
        assert summary.skipped == 0
        assert summary.succeeded


def test_pipeline_skips_cached_source():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        home = root / "home.itl"

        home.write_text(
            "page $home {}",
            encoding="utf-8",
        )

        cache = Cache(root)

        cache.put(
            str(home),
            output="generated",
        )

        cache.save()

        graph = DependencyGraph()

        graph.add_node(str(home))

        executed = []

        def builder(item):

            executed.append(
                item.source
            )

        pipeline = BuildPipeline(
            BuildPlanner(
                CacheDecider(cache),
                graph,
            ),
            BuildExecutor(
                builder
            ),
        )

        outcome = pipeline.build(
            [home]
        )

        assert outcome.plan.items == []
        assert outcome.results.results == []

        assert outcome.summary.processed == 0
        assert outcome.summary.successful == 0
        assert outcome.summary.failed == 0
        assert outcome.summary.skipped == 1
        assert outcome.summary.succeeded

        assert executed == []



if __name__ == "__main__":

    test_pipeline_builds_plan_and_executes()

    test_pipeline_skips_cached_source()

    print(
        "All build pipeline tests passed."
    )