from pathlib import Path
from tempfile import TemporaryDirectory

from itl.build.planner import BuildPlanner
from itl.cache.cache import Cache
from itl.cache.decider import CacheDecider
from itl.cache.decision import CacheStatus
from itl.graph.graph import DependencyGraph


def write_source(
    root: Path,
    name: str,
    content: str,
):

    path = root / name

    path.write_text(
        content,
        encoding="utf-8",
    )

    return str(path)


def test_incremental_build_flow():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        navigation = write_source(
            root,
            "navigation.itl",
            "import navigation",
        )

        home = write_source(
            root,
            "home.itl",
            "import navigation",
        )

        checkout = write_source(
            root,
            "checkout.itl",
            "import home",
        )

        footer = write_source(
            root,
            "footer.itl",
            "footer",
        )

        sources = [
            navigation,
            home,
            checkout,
            footer,
        ]

        cache = Cache(root)

        # First build: nothing is cached.
        graph = DependencyGraph()

        graph.add_dependency(
            home,
            navigation,
        )

        graph.add_dependency(
            checkout,
            home,
        )

        graph.add_node(footer)

        planner = BuildPlanner(
            CacheDecider(cache),
            graph,
        )

        plan = planner.plan(sources)

        assert set(plan.sources) == set(
            sources
        )

        assert all(
            item.status == CacheStatus.MISS
            for item in plan.items
        )

        # Simulate successful generation.
        for source in sources:

            cache.put(
                source,
                output=f"generated:{source}",
            )

        cache.save()

        # Second build: everything should be cached.
        planner = BuildPlanner(
            CacheDecider(cache),
            graph,
        )

        plan = planner.plan(sources)

        assert plan.items == []

        # Change navigation.
        Path(navigation).write_text(
            "import navigation\nupdated",
            encoding="utf-8",
        )

        # navigation changed.
        # home depends on navigation.
        # checkout depends on home.
        # footer is independent.
        planner = BuildPlanner(
            CacheDecider(cache),
            graph,
        )

        plan = planner.plan(sources)

        planned = {
            item.source
            for item in plan.items
        }

        assert planned == {
            navigation,
            home,
            checkout,
        }

        assert footer not in planned

        navigation_item = next(
            item
            for item in plan.items
            if item.source == navigation
        )

        assert (
            navigation_item.status
            == CacheStatus.INVALIDATED
        )

        # Change only footer.
        Path(footer).write_text(
            "footer updated",
            encoding="utf-8",
        )

        planner = BuildPlanner(
            CacheDecider(cache),
            graph,
        )

        plan = planner.plan(sources)

        planned = {
            item.source
            for item in plan.items
        }

        assert planned == {
            navigation,
            home,
            checkout,
            footer,
        }


if __name__ == "__main__":

    test_incremental_build_flow()

    print(
        "All build integration tests passed."
    )