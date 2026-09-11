from collections.abc import Callable

from itl.build.models import BuildItem, BuildPlan
from itl.build.results import (
    BuildResult,
    BuildResults,
    BuildResultStatus,
)
from itl.build.scheduler import BuildScheduler
from itl.repair.interfaces import Repairer
from itl.validation.models import ValidationContext
from itl.validation.pipeline import ValidatorPipeline
from itl.validation.errors import ValidationFailure


class BuildExecutor:

    def __init__(
        self,
        builder: Callable[[BuildItem], object],
        scheduler: BuildScheduler | None = None,
        validator: ValidatorPipeline | None = None,
        validation_context_factory: Callable[[BuildItem, object], ValidationContext] | None = None,
        repairer: Repairer | None = None,
    ):
        self.builder = builder
        self.scheduler = scheduler or BuildScheduler()
        self.validator = validator
        self.validation_context_factory = validation_context_factory
        self.repairer = repairer

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
                    validation_report = None
                    if self.validator is not None:
                        context = (
                            self.validation_context_factory(item, output)
                            if self.validation_context_factory is not None
                            else ValidationContext(
                                unit_id=source,
                                source=source,
                                output=output,
                            )
                        )
                        validation_report = self.validator.validate(context)
                        if not validation_report.passed:
                            if self.repairer is not None:
                                repair_result = self.repairer.repair(
                                    item,
                                    str(output),
                                    validation_report,
                                )
                                if repair_result.succeeded:
                                    results.add(
                                        BuildResult(
                                            source=source,
                                            status=BuildResultStatus.SUCCESS,
                                            output=repair_result.output,
                                            validation_report=repair_result.validation_report,
                                        )
                                    )
                                    continue
                                output = repair_result.output
                                validation_report = repair_result.validation_report or validation_report
                                error = RuntimeError(
                                    repair_result.error or "Repair failed."
                                )
                            else:
                                error = ValidationFailure(validation_report)
                            results.add(
                                BuildResult(
                                    source=source,
                                    status=BuildResultStatus.FAILED,
                                    output=output,
                                    error=error,
                                    validation_report=validation_report,
                                )
                            )
                            continue

                    results.add(
                        BuildResult(
                            source=source,
                            status=BuildResultStatus.SUCCESS,
                            output=output,
                            validation_report=validation_report,
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
