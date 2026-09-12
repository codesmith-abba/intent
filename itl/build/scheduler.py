from dataclasses import dataclass
import heapq

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
    """Determine dependency-safe, deterministic build batches."""

    def schedule(
        self,
        plan: BuildPlan,
        completed: set[str] | None = None,
    ) -> BuildSchedule:
        completed = set(completed or ())
        items = {item.source: item for item in plan.items}
        plan_order = {
            item.source: index
            for index, item in enumerate(plan.items)
        }
        remaining = set(items) - completed

        dependents: dict[str, set[str]] = {source: set() for source in items}
        indegree: dict[str, int] = {source: 0 for source in remaining}
        for source in remaining:
            for dependency in items[source].dependencies:
                if dependency in remaining:
                    indegree[source] += 1
                    dependents.setdefault(dependency, set()).add(source)

        ready = [
            source
            for source in remaining
            if indegree[source] == 0
        ]
        ready_heap = [(plan_order[source], source) for source in ready]
        heapq.heapify(ready_heap)
        batches: list[BuildBatch] = []
        scheduled = 0

        while ready_heap:
            batch_sources: list[str] = []
            current = []
            while ready_heap:
                _, source = heapq.heappop(ready_heap)
                current.append(source)

            current.sort(key=plan_order.__getitem__)
            batch_sources.extend(current)
            batches.append(BuildBatch(tuple(batch_sources)))
            scheduled += len(batch_sources)

            next_ready: list[str] = []
            for source in batch_sources:
                for dependent in dependents.get(source, ()):
                    indegree[dependent] -= 1
                    if indegree[dependent] == 0:
                        next_ready.append(dependent)
            for source in next_ready:
                heapq.heappush(ready_heap, (plan_order[source], source))

        if scheduled != len(remaining):
            raise ValueError("Build plan contains a dependency cycle.")

        return BuildSchedule(tuple(batches))
