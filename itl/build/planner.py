from itl.build.models import BuildItem, BuildPlan
from itl.cache.decider import CacheDecider
from itl.cache.decision import CacheStatus
from itl.graph.graph import DependencyGraph


class BuildPlanner:

    def __init__(
        self,
        decider: CacheDecider,
        graph: DependencyGraph,
    ):

        self.decider = decider
        self.graph = graph

    def plan(
        self,
        sources: list[str],
    ) -> BuildPlan:

        decisions = {}

        for source in sources:

            decisions[source] = (
                self.decider.decide(source)
            )

        affected = set()

        for source, decision in decisions.items():

            if decision.status in {
                CacheStatus.MISS,
                CacheStatus.INVALIDATED,
            }:

                affected.update(
                    self.graph.affected_by(source)
                )

        plan = BuildPlan()

        for source in sources:

            if source not in affected:
                continue

            decision = decisions.get(source)

            if decision is None:

                decision = self.decider.decide(
                    source
                )

            dependencies = (
                self.graph.dependencies_of(
                    source
                )
            )

            plan.add(
                BuildItem(
                    source=source,
                    status=decision.status,
                    dependencies=dependencies,
                )
            )

        order = self.graph.topological_order()

        return BuildPlan(
            items=plan.ordered(order)
        )