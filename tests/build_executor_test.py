from itl.build.executor import BuildExecutor
from itl.build.models import BuildItem, BuildPlan
from itl.cache.decision import CacheStatus


def test_executor_runs_items_in_order():

    executed = []

    def builder(item):

        executed.append(item.source)

        return f"generated:{item.source}"

    plan = BuildPlan()

    plan.add(
        BuildItem(
            source="navigation.itl",
            status=CacheStatus.MISS,
        )
    )

    plan.add(
        BuildItem(
            source="home.itl",
            status=CacheStatus.INVALIDATED,
        )
    )

    plan.add(
        BuildItem(
            source="checkout.itl",
            status=CacheStatus.INVALIDATED,
        )
    )

    executor = BuildExecutor(builder)

    results = executor.execute(plan)

    assert executed == [
        "navigation.itl",
        "home.itl",
        "checkout.itl",
    ]

    assert len(results.successful) == 3
    assert len(results.failed) == 0


def test_executor_does_nothing_for_empty_plan():

    executed = []

    def builder(item):

        executed.append(item.source)

    executor = BuildExecutor(builder)

    executor.execute(
        BuildPlan()
    )

    assert executed == []

def test_executor_records_failed_build():

    def builder(item):

        if item.source == "home.itl":
            raise RuntimeError(
                "generation failed"
            )

        return f"generated:{item.source}"

    plan = BuildPlan()

    plan.add(
        BuildItem(
            source="navigation.itl",
            status=CacheStatus.MISS,
        )
    )

    plan.add(
        BuildItem(
            source="home.itl",
            status=CacheStatus.INVALIDATED,
        )
    )

    executor = BuildExecutor(builder)

    results = executor.execute(plan)

    assert len(results.successful) == 1
    assert len(results.failed) == 1

    assert (
        results.failed[0].source
        == "home.itl"
    )

    assert isinstance(
        results.failed[0].error,
        RuntimeError,
    )

def test_executor_does_nothing_for_empty_plan():

    executed = []

    def builder(item):

        executed.append(item.source)

    executor = BuildExecutor(builder)

    results = executor.execute(
        BuildPlan()
    )

    assert executed == []

    assert results.results == []
    assert results.succeeded


if __name__ == "__main__":

    test_executor_runs_items_in_order()
    test_executor_does_nothing_for_empty_plan()

    print(
        "All build executor tests passed."
    )