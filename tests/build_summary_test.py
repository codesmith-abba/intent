from itl.build.results import (
    BuildResult,
    BuildResults,
    BuildResultStatus,
)
from itl.build.summary import summarize


def test_summary():

    results = BuildResults()

    results.add(
        BuildResult(
            source="navigation.itl",
            status=BuildResultStatus.SUCCESS,
        )
    )

    results.add(
        BuildResult(
            source="home.itl",
            status=BuildResultStatus.SUCCESS,
        )
    )

    results.add(
        BuildResult(
            source="checkout.itl",
            status=BuildResultStatus.FAILED,
            error=RuntimeError("failed"),
        )
    )

    summary = summarize(
        results,
        total_sources=4,
    )

    assert summary.processed == 3
    assert summary.successful == 2
    assert summary.failed == 1
    assert summary.skipped == 1

    assert not summary.succeeded


def test_all_successful():

    results = BuildResults()

    results.add(
        BuildResult(
            source="home.itl",
            status=BuildResultStatus.SUCCESS,
        )
    )

    summary = summarize(
        results,
        total_sources=1,
    )

    assert summary.processed == 1
    assert summary.successful == 1
    assert summary.failed == 0
    assert summary.skipped == 0
    assert summary.succeeded


def test_all_skipped():

    results = BuildResults()

    summary = summarize(
        results,
        total_sources=3,
    )

    assert summary.processed == 0
    assert summary.successful == 0
    assert summary.failed == 0
    assert summary.skipped == 3
    assert summary.succeeded


if __name__ == "__main__":

    test_summary()
    test_all_successful()
    test_all_skipped()

    print(
        "All build summary tests passed."
    )