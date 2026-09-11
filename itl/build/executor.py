from collections.abc import Callable

from itl.build.models import BuildItem, BuildPlan
from itl.build.results import (
    BuildResult,
    BuildResults,
    BuildResultStatus,
)
from itl.build.scheduler import BuildScheduler


class BuildExecutor:

    def __init__(
        self,
        builder: Callable[[BuildItem], object],
        scheduler: BuildScheduler | None = None,
    ):
        self.builder = builder
        self.scheduler = scheduler or BuildScheduler()

    def execute(
        self,
        plan: BuildPlan,
        previous_results: BuildResults | None = None,
    ) -> BuildResults:
        results = BuildResults()

        if previous_results is not None:
            for result in previous_results.results:
                if result.status == BuildResultStatus.SUCCESS:
                    results.add(result)

        completed = {
            result.source
            for result in results.successful
        }
        schedule = self.scheduler.schedule(plan, completed=completed)
        items = {item.source: item for item in plan.items}

        for batch in schedule.batches:
            for source in batch.items:
                item = items[source]
                dependency_results = {
                    result.source: result
                    for result in results.results
                }

                blocked = any(
                    dependency in dependency_results
                    and dependency_results[dependency].status
                    != BuildResultStatus.SUCCESS
                    for dependency in item.dependencies
                )

                if blocked:
                    results.add(
                        BuildResult(
                            source=source,
                            status=BuildResultStatus.SKIPPED,
                        )
                    )
                    continue

                try:
                    output = self.builder(item)
                    results.add(
                        BuildResult(
                            source=source,
                            status=BuildResultStatus.SUCCESS,
                            output=output,
                        )
                    )
                except Exception as error:
                    results.add(
                        BuildResult(
                            source=source,
                            status=BuildResultStatus.FAILED,
                            error=error,
                        )
                    )

        return results
