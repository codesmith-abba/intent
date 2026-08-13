from pathlib import Path
from tempfile import TemporaryDirectory

from itl.build.planner import BuildPlanner
from itl.cache.cache import Cache
from itl.cache.decider import CacheDecider
from itl.cache.decision import CacheStatus
from itl.graph.graph import DependencyGraph


def create_source(
    root: Path,
    name: str,
):

    path = root / name

    path.write_text(
        f"source {name}",
        encoding="utf-8",
    )

    return str(path)


def test_new_source_is_planned():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        home = create_source(
            root,
            "home.itl",
        )

        cache = Cache(root)

        graph = DependencyGraph()

        graph.add_node(home)

        planner = BuildPlanner(
            CacheDecider(cache),
            graph,
        )

        plan = planner.plan([home])

        assert len(plan.items) == 1

        assert plan.items[0].source == home

        assert (
            plan.items[0].status
            == CacheStatus.MISS
        )


def test_changed_source_affects_dependents():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        navigation = create_source(
            root,
            "navigation.itl",
        )

        home = create_source(
            root,
            "home.itl",
        )

        checkout = create_source(
            root,
            "checkout.itl",
        )

        cache = Cache(root)

        cache.put(navigation)
        cache.put(home)
        cache.put(checkout)

        cache.save()

        graph = DependencyGraph()

        graph.add_dependency(
            home,
            navigation,
        )

        graph.add_dependency(
            checkout,
            home,
        )

        navigation_path = Path(
            navigation
        )

        navigation_path.write_text(
            "changed navigation",
            encoding="utf-8",
        )

        planner = BuildPlanner(
            CacheDecider(cache),
            graph,
        )

        plan = planner.plan(
            [
                navigation,
                home,
                checkout,
            ]
        )

        planned = set(plan.sources)

        assert navigation in planned
        assert home in planned
        assert checkout in planned


def test_unchanged_unaffected_source_is_skipped():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        home = create_source(
            root,
            "home.itl",
        )

        footer = create_source(
            root,
            "footer.itl",
        )

        cache = Cache(root)

        cache.put(home)
        cache.put(footer)

        cache.save()

        graph = DependencyGraph()

        graph.add_node(home)
        graph.add_node(footer)

        planner = BuildPlanner(
            CacheDecider(cache),
            graph,
        )

        plan = planner.plan(
            [
                home,
                footer,
            ]
        )

        assert plan.items == []

def test_planner_returns_dependency_order():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        navigation = create_source(
            root,
            "navigation.itl",
        )

        home = create_source(
            root,
            "home.itl",
        )

        checkout = create_source(
            root,
            "checkout.itl",
        )

        cache = Cache(root)

        graph = DependencyGraph()

        graph.add_dependency(
            home,
            navigation,
        )

        graph.add_dependency(
            checkout,
            home,
        )

        planner = BuildPlanner(
            CacheDecider(cache),
            graph,
        )

        plan = planner.plan(
            [
                checkout,
                home,
                navigation,
            ]
        )

        assert plan.sources == [
            navigation,
            home,
            checkout,
        ]

if __name__ == "__main__":

    test_new_source_is_planned()

    test_changed_source_affects_dependents()

    test_unchanged_unaffected_source_is_skipped()
    test_planner_returns_dependency_order()

    print(
        "All build planner tests passed."
    )