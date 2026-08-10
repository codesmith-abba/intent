from dataclasses import dataclass, field


@dataclass(slots=True)
class GraphNode:

    id: str

    dependencies: set[str] = field(
        default_factory=set
    )

    dependents: set[str] = field(
        default_factory=set
    )

class DependencyGraph:

    def __init__(self):

        self.nodes: dict[str, GraphNode] = {}
    
    def has_node(
        self,
        node_id: str,
    ) -> bool:

        return node_id in self.nodes

    def add_node(self, node_id: str) -> GraphNode:

        if node_id not in self.nodes:

            self.nodes[node_id] = GraphNode(
                id=node_id
            )

        return self.nodes[node_id]

    def add_dependency(
        self,
        node_id: str,
        dependency_id: str,
    ):

        if node_id == dependency_id:

            raise ValueError(
                f"Node '{node_id}' cannot depend on itself."
            )

        self.add_node(node_id)
        self.add_node(dependency_id)

        if self._has_path(
            dependency_id,
            node_id,
        ):

            raise ValueError(
                f"Dependency cycle detected: "
                f"'{node_id}' -> '{dependency_id}'."
            )

        self.nodes[node_id].dependencies.add(
            dependency_id
        )

        self.nodes[dependency_id].dependents.add(
            node_id
        )
    
    def remove_node(
        self,
        node_id: str,
    ):
        node = self.nodes.pop(
            node_id,
            None,
        )

        if node is None:
            return

        for dependency_id in node.dependencies:

            dependency = self.nodes.get(
                dependency_id
            )

            if dependency:

                dependency.dependents.discard(
                    node_id
                )

        for dependent_id in node.dependents:

            dependent = self.nodes.get(
                dependent_id
            )

            if dependent:

                dependent.dependencies.discard(
                    node_id
                )
    
    def clear(self):
        self.nodes.clear()
    
    def dependencies_of(
        self,
        node_id: str,
    ) -> set[str]:

        node = self.nodes.get(node_id)

        if node is None:
            return set()

        return set(node.dependencies)
    
    def dependents_of(
        self,
        node_id: str,
    ) -> set[str]:

        node = self.nodes.get(node_id)

        if node is None:
            return set()

        return set(node.dependents)
    
    def depends_on(
        self,
        node_id: str,
        dependency_id: str,
    ) -> bool:

        node = self.nodes.get(node_id)

        if node is None:
            return False

        return dependency_id in node.dependencies
    
    def transitively_depends_on(
        self,
        node_id: str,
        dependency_id: str,
    ) -> bool:

        if node_id not in self.nodes:
            return False

        if dependency_id not in self.nodes:
            return False

        visited = set()
        stack = list(
            self.nodes[node_id].dependencies
        )

        while stack:

            current = stack.pop()

            if current == dependency_id:
                return True

            if current in visited:
                continue

            visited.add(current)

            stack.extend(
                self.nodes[current].dependencies
            )

        return False
    
    def affected_by(
        self,
        node_id: str,
    ) -> set[str]:

        if node_id not in self.nodes:
            return set()

        affected = set()
        stack = [node_id]

        while stack:

            current = stack.pop()

            if current in affected:
                continue

            affected.add(current)

            for dependent in self.dependents_of(
                current
            ):
                stack.append(dependent)

        return affected
    
    def topological_order(self) -> list[str]:

        indegree = {
            node_id: len(node.dependencies)
            for node_id, node in self.nodes.items()
        }

        queue = [
            node_id
            for node_id, degree in indegree.items()
            if degree == 0
        ]

        order = []

        while queue:

            current = queue.pop(0)

            order.append(current)

            for dependent in self.nodes[
                current
            ].dependents:

                indegree[dependent] -= 1

                if indegree[dependent] == 0:

                    queue.append(dependent)

        if len(order) != len(self.nodes):

            raise ValueError(
                "Dependency graph contains a cycle."
            )

        return order
        
    def _has_path(
        self,
        start: str,
        target: str,
        visited: set[str] | None = None,
    ) -> bool:

        if visited is None:
            visited = set()

        if start == target:
            return True

        if start in visited:
            return False

        visited.add(start)

        node = self.nodes.get(start)

        if node is None:
            return False

        for dependency_id in node.dependencies:

            if self._has_path(
                dependency_id,
                target,
                visited,
            ):
                return True

        return False
    
    def __repr__(self) -> str:

        lines = ["DependencyGraph:"]

        for node_id in sorted(self.nodes):

            node = self.nodes[node_id]

            lines.append(
                f"  {node.id}"
            )

            if node.dependencies:

                lines.append(
                    f"    dependencies: "
                    f"{sorted(node.dependencies)}"
                )

            if node.dependents:

                lines.append(
                    f"    dependents: "
                    f"{sorted(node.dependents)}"
                )

        return "\n".join(lines)
