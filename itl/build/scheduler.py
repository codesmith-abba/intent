from dataclasses import dataclass

from itl.build.models import BuildPlan


@dataclass(frozen=True, slots=True)
class BuildBatch:
    """A deterministic set of build items that may execute independently."""

    items: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BuildSchedule:
    """Dependency-safe execution batches for a build plan."""

    batches: tuple[BuildBatch, ...]

    @property
    def sources(self) -> tuple[str, ...]:
        return tuple(
            source
            for batch in self.batches
            for source in batch.items
        )


class BuildScheduler:
    """Determine dependency-safe, future-parallel build batches."""

    def schedule(
        self,
        plan: BuildPlan,
        completed: set[str] | None = None,
    ) -> BuildSchedule:
        completed = set(completed or ())
        items = {item.source: item for item in plan.items}

        # Dependencies outside the current plan are assumed to be already
        # available (for example, cache hits that were not scheduled).
        remaining = set(items) - completed
        batches: list[BuildBatch] = []

        while remaining:
            ready = sorted(
                source
                for source in remaining
                if all(
                    dependency not in remaining
                    for dependency in items[source].dependencies
                )
            )

            if not ready:
                raise ValueError("Build plan contains a dependency cycle.")

            batches.append(BuildBatch(tuple(ready)))
            completed.update(ready)
            remaining.difference_update(ready)

        return BuildSchedule(tuple(batches))
