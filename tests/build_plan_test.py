from itl.build.models import BuildItem, BuildPlan
from itl.cache.decision import CacheStatus


def test_build_item():

    item = BuildItem(
        source="home.itl",
        status=CacheStatus.INVALIDATED,
    )

    assert item.source == "home.itl"

    assert (
        item.status
        == CacheStatus.INVALIDATED
    )

    assert item.dependencies == set()


def test_build_item_dependencies():

    item = BuildItem(
        source="home.itl",
        status=CacheStatus.INVALIDATED,
        dependencies={
            "navigation.itl",
            "footer.itl",
        },
    )

    assert item.dependencies == {
        "navigation.itl",
        "footer.itl",
    }


def test_build_plan():

    plan = BuildPlan()

    plan.add(
        BuildItem(
            source="home.itl",
            status=CacheStatus.INVALIDATED,
        )
    )

    plan.add(
        BuildItem(
            source="navigation.itl",
            status=CacheStatus.HIT,
        )
    )

    assert len(plan.items) == 2

    assert plan.sources == [
        "home.itl",
        "navigation.itl",
    ]

def test_build_plan_ordering():

    plan = BuildPlan()

    plan.add(
        BuildItem(
            source="checkout.itl",
            status=CacheStatus.INVALIDATED,
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
            source="navigation.itl",
            status=CacheStatus.INVALIDATED,
        )
    )

    ordered = plan.ordered(
        [
            "navigation.itl",
            "home.itl",
            "checkout.itl",
        ]
    )

    assert [
        item.source
        for item in ordered
    ] == [
        "navigation.itl",
        "home.itl",
        "checkout.itl",
    ]


if __name__ == "__main__":

    test_build_item()
    test_build_item_dependencies()
    test_build_plan()
    test_build_plan_ordering()

    print(
        "All build plan tests passed."
    )