from collections.abc import Callable

from itl.build.models import BuildItem, BuildPlan
from itl.build.results import (
    BuildResult,
    BuildResults,
    BuildResultStatus,
)


class BuildExecutor:

    def __init__(
        self,
        builder: Callable[[BuildItem], object],
    ):

        self.builder = builder

    def execute(
        self,
        plan: BuildPlan,
    ) -> BuildResults:

        results = BuildResults()

        for item in plan.items:

            try:

                output = self.builder(item)

                results.add(
                    BuildResult(
                        source=item.source,
                        status=BuildResultStatus.SUCCESS,
                        output=output,
                    )
                )

            except Exception as error:

                results.add(
                    BuildResult(
                        source=item.source,
                        status=BuildResultStatus.FAILED,
                        error=error,
                    )
                )

        return results