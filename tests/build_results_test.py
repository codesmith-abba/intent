from itl.build.results import (
    BuildResult,
    BuildResults,
    BuildResultStatus,
)


def test_successful_results():

    results = BuildResults()

    results.add(
        BuildResult(
            source="home.itl",
            status=BuildResultStatus.SUCCESS,
            output="generated home",
        )
    )

    assert len(results.results) == 1
    assert len(results.successful) == 1
    assert len(results.failed) == 0
    assert results.succeeded


def test_failed_results():

    error = RuntimeError(
        "generation failed"
    )

    results = BuildResults()

    results.add(
        BuildResult(
            source="home.itl",
            status=BuildResultStatus.FAILED,
            error=error,
        )
    )

    assert len(results.successful) == 0
    assert len(results.failed) == 1
    assert not results.succeeded

    assert (
        results.failed[0].error
        is error
    )


def test_mixed_results():

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
            status=BuildResultStatus.FAILED,
            error=RuntimeError("failed"),
        )
    )

    assert len(results.successful) == 1
    assert len(results.failed) == 1
    assert not results.succeeded


if __name__ == "__main__":

    test_successful_results()
    test_failed_results()
    test_mixed_results()

    print(
        "All build results tests passed."
    )