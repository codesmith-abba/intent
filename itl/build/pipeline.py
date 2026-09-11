from pathlib import Path

from itl.build.executor import BuildExecutor
from itl.build.planner import BuildPlanner
from itl.build.outcome import BuildOutcome
from itl.build.summary import summarize
from itl.gir.changes import GIRChangeDetector
from itl.gir.store import GIRFingerprintStore


class BuildPipeline:

    def __init__(
        self,
        planner: BuildPlanner,
        executor: BuildExecutor,
        gir_store: GIRFingerprintStore | None = None,
    ):
        self.planner = planner
        self.executor = executor
        self.gir_store = gir_store

    def build(
        self,
        sources: list[str | Path],
        gir_fingerprints: dict[str, str] | None = None,
        previous_dependents: dict[str, set[str]] | None = None,
    ) -> BuildOutcome:
        sources = [str(source) for source in sources]
        gir_changes = None

        if self.gir_store is not None and gir_fingerprints is not None:
            previous = self.gir_store.load()
            gir_changes = GIRChangeDetector.detect(previous, gir_fingerprints)

        plan = self.planner.plan(
            sources,
            gir_changes=gir_changes,
            previous_dependents=previous_dependents,
        )
        results = self.executor.execute(plan)

        if (
            self.gir_store is not None
            and gir_fingerprints is not None
            and results.succeeded
        ):
            self.gir_store.save(gir_fingerprints)

        summary = summarize(results, total_sources=len(sources))
        return BuildOutcome(plan=plan, results=results, summary=summary)
