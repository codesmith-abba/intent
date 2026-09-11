"""Dependency-aware invalidation for changed GIR nodes."""

from itl.graph.graph import DependencyGraph

from .changes import GIRChangeSet


class GIRDependencyInvalidator:
    """Expand GIR changes through the repository's existing dependency graph."""

    def __init__(self, graph: DependencyGraph):
        self.graph = graph

    def affected_nodes(
        self,
        changes: GIRChangeSet,
        *,
        previous_dependents: dict[str, set[str]] | None = None,
    ) -> set[str]:
        """Return changed nodes and their transitive dependents.

        Removed nodes no longer exist in the current graph, so callers that
        mutate the graph before invalidation may provide the removed node's
        previously-known dependents. The dependency graph itself remains the
        single graph implementation used for traversal.
        """
        affected: set[str] = set()
        previous_dependents = previous_dependents or {}

        for change in changes.added + changes.modified:
            affected.update(self.graph.affected_by(change.node_id))

        for change in changes.removed:
            affected.update(previous_dependents.get(change.node_id, set()))

        return affected
