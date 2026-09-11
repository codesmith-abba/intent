from itl.build.models import BuildItem, BuildPlan
from itl.cache.decider import CacheDecider
from itl.cache.decision import CacheStatus
from itl.graph.graph import DependencyGraph
from itl.gir.changes import GIRChangeSet
from itl.gir.invalidation import GIRDependencyInvalidator


class BuildPlanner:

    def __init__(
        self,
        decider: CacheDecider,
        graph: DependencyGraph,
    ):
        self.decider = decider
        self.graph = graph
        self.gir_invalidator = GIRDependencyInvalidator(graph)

    def plan(
        self,
        sources: list[str],
        gir_changes: GIRChangeSet | None = None,
        previous_dependents: dict[str, set[str]] | None = None,
    ) -> BuildPlan:
        decisions = {}

        for source in sources:
            decisions[source] = self.decider.decide(source)

        affected = set()

        if gir_changes is None:
            for source, decision in decisions.items():
                if decision.status in {
                    CacheStatus.MISS,
                    CacheStatus.INVALIDATED,
                }:
                    affected.update(self.graph.affected_by(source))
        else:
            affected.update(
                self.gir_invalidator.affected_nodes(
                    gir_changes,
                    previous_dependents=previous_dependents,
                )
            )

        removed = []

        if gir_changes is not None:
            removed = sorted(
                change.node_id
                for change in gir_changes.removed
            )

        plan = BuildPlan(removed=removed)

        for source in sources:
            if source not in affected:
                continue

            decision = decisions.get(source)

            if decision is None:
                decision = self.decider.decide(source)

            dependencies = self.graph.dependencies_of(source)

            plan.add(
                BuildItem(
                    source=source,
                    status=decision.status,
                    dependencies=dependencies,
                )
            )

        order = self.graph.topological_order()

        return plan.ordered(order)
