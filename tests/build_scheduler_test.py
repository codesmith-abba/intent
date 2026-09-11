from itl.build.executor import BuildExecutor
from itl.build.models import BuildItem, BuildPlan
from itl.build.results import BuildResult, BuildResults, BuildResultStatus
from itl.build.scheduler import BuildScheduler
from itl.cache.decision import CacheStatus


def item(source, dependencies=()):
    return BuildItem(source=source, status=CacheStatus.MISS, dependencies=set(dependencies))


def plan(*items):
    return BuildPlan(items=list(items))


def test_dependency_ordering():
    schedule = BuildScheduler().schedule(plan(item("b", ["a"]), item("a")))
    assert schedule.batches[0].items == ("a",)
    assert schedule.batches[1].items == ("b",)


def test_independent_nodes_share_batch():
    schedule = BuildScheduler().schedule(plan(item("a"), item("b"), item("c")))
    assert schedule.batches == (schedule.batches[0],)
    assert schedule.batches[0].items == ("a", "b", "c")


def test_multiple_scheduling_levels():
    schedule = BuildScheduler().schedule(
        plan(item("d", ["b", "c"]), item("b", ["a"]), item("c", ["a"]), item("a"))
    )
    assert [batch.items for batch in schedule.batches] == [("a",), ("b", "c"), ("d",)]


def test_failed_dependency_skips_dependent_work():
    calls = []

    def builder(build_item):
        calls.append(build_item.source)
        if build_item.source == "a":
            raise RuntimeError("boom")
        return build_item.source

    results = BuildExecutor(builder).execute(plan(item("a"), item("b", ["a"]), item("c")))
    assert calls == ["a", "c"]
    assert [result.source for result in results.failed] == ["a"]
    assert [result.source for result in results.skipped] == ["b"]


def test_skipped_dependency_skips_transitive_dependents():
    def builder(build_item):
        if build_item.source == "a":
            raise RuntimeError("boom")
        return build_item.source

    results = BuildExecutor(builder).execute(
        plan(item("a"), item("b", ["a"]), item("c", ["b"]))
    )
    assert [result.source for result in results.failed] == ["a"]
    assert [result.source for result in results.skipped] == ["b", "c"]


def test_resume_skips_successful_previous_work():
    calls = []
    previous = BuildResults(results=[BuildResult("a", BuildResultStatus.SUCCESS, output="cached")])

    def builder(build_item):
        calls.append(build_item.source)
        return build_item.source

    results = BuildExecutor(builder).execute(
        plan(item("a"), item("b", ["a"])), previous_results=previous
    )
    assert calls == ["b"]
    assert [result.source for result in results.successful] == ["a", "b"]


def test_cycle_is_rejected():
    cyclic = plan(item("a", ["b"]), item("b", ["a"]))
    try:
        BuildScheduler().schedule(cyclic)
    except ValueError as error:
        assert "cycle" in str(error).lower()
    else:
        raise AssertionError("Expected cycle protection")


def test_empty_plan():
    schedule = BuildScheduler().schedule(BuildPlan())
    assert schedule.batches == ()
    assert schedule.sources == ()


def test_single_node_plan():
    schedule = BuildScheduler().schedule(plan(item("a")))
    assert [batch.items for batch in schedule.batches] == [("a",)]


def test_external_dependency_is_already_resolved():
    schedule = BuildScheduler().schedule(plan(item("b", ["a"])))
    assert schedule.sources == ("b",)


def test_schedule_is_deterministic():
    scheduler = BuildScheduler()
    build_plan = plan(item("c"), item("a"), item("b", ["a"]))
    assert scheduler.schedule(build_plan) == scheduler.schedule(build_plan)


if __name__ == "__main__":
    test_dependency_ordering()
    test_independent_nodes_share_batch()
    test_multiple_scheduling_levels()
    test_failed_dependency_skips_dependent_work()
    test_skipped_dependency_skips_transitive_dependents()
    test_resume_skips_successful_previous_work()
    test_cycle_is_rejected()
    test_empty_plan()
    test_single_node_plan()
    test_external_dependency_is_already_resolved()
    test_schedule_is_deterministic()
    print("Build scheduler tests passed.")
