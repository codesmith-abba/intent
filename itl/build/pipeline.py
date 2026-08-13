from pathlib import Path

from itl.build.executor import BuildExecutor
from itl.build.planner import BuildPlanner
from itl.build.outcome import BuildOutcome
from itl.build.summary import summarize


class BuildPipeline:

    def __init__(
        self,
        planner: BuildPlanner,
        executor: BuildExecutor,
    ):

        self.planner = planner
        self.executor = executor

    def build(
        self,
        sources: list[str | Path],
    ) -> BuildOutcome:

        sources = [
            str(source)
            for source in sources
        ]

        plan = self.planner.plan(
            sources
        )

        results = self.executor.execute(
            plan
        )

        summary = summarize(
            results,
            total_sources=len(sources),
        )

        return BuildOutcome(
            plan=plan,
            results=results,
            summary=summary,
        )