from itl.graph.graph import DependencyGraph


def test_add_nodes():

    graph = DependencyGraph()

    home = graph.add_node("home")

    assert home.id == "home"
    assert graph.has_node("home")


def test_add_dependency():

    graph = DependencyGraph()

    graph.add_dependency(
        "home",
        "navigation",
    )

    assert graph.depends_on(
        "home",
        "navigation",
    )

    assert "home" in graph.dependents_of(
        "navigation"
    )

    assert "navigation" in graph.dependencies_of(
        "home"
    )


def test_multiple_dependencies():

    graph = DependencyGraph()

    graph.add_dependency(
        "home",
        "navigation",
    )

    graph.add_dependency(
        "home",
        "footer",
    )

    assert graph.dependencies_of(
        "home"
    ) == {
        "navigation",
        "footer",
    }

    assert graph.dependents_of(
        "navigation"
    ) == {"home"}

    assert graph.dependents_of(
        "footer"
    ) == {"home"}


def test_self_dependency():

    graph = DependencyGraph()

    try:

        graph.add_dependency(
            "home",
            "home",
        )

        assert False, (
            "Expected self-dependency error"
        )

    except ValueError:
        pass


def test_cycle_detection():

    graph = DependencyGraph()

    graph.add_dependency(
        "home",
        "navigation",
    )

    graph.add_dependency(
        "navigation",
        "header",
    )

    try:

        graph.add_dependency(
            "header",
            "home",
        )

        assert False, (
            "Expected cycle detection"
        )

    except ValueError:
        pass


def test_affected_by():

    graph = DependencyGraph()

    graph.add_dependency(
        "home",
        "navigation",
    )

    graph.add_dependency(
        "home",
        "footer",
    )

    graph.add_dependency(
        "checkout",
        "home",
    )

    affected = graph.affected_by(
        "navigation"
    )

    assert affected == {
        "navigation",
        "home",
        "checkout",
    }


def test_direct_dependency():

    graph = DependencyGraph()

    graph.add_dependency(
        "checkout",
        "home",
    )

    graph.add_dependency(
        "home",
        "navigation",
    )

    assert graph.depends_on(
        "checkout",
        "home",
    )

    assert not graph.depends_on(
        "checkout",
        "navigation",
    )


def test_transitive_dependency():

    graph = DependencyGraph()

    graph.add_dependency(
        "checkout",
        "home",
    )

    graph.add_dependency(
        "home",
        "navigation",
    )

    assert graph.transitively_depends_on(
        "checkout",
        "home",
    )

    assert graph.transitively_depends_on(
        "checkout",
        "navigation",
    )

    assert not graph.transitively_depends_on(
        "navigation",
        "checkout",
    )


def test_topological_order():

    graph = DependencyGraph()

    graph.add_dependency(
        "home",
        "navigation",
    )

    graph.add_dependency(
        "home",
        "footer",
    )

    graph.add_dependency(
        "checkout",
        "home",
    )

    order = graph.topological_order()

    assert order.index(
        "navigation"
    ) < order.index(
        "home"
    )

    assert order.index(
        "footer"
    ) < order.index(
        "home"
    )

    assert order.index(
        "home"
    ) < order.index(
        "checkout"
    )


def test_remove_node():

    graph = DependencyGraph()

    graph.add_dependency(
        "home",
        "navigation",
    )

    graph.add_dependency(
        "home",
        "footer",
    )

    graph.remove_node(
        "navigation"
    )

    assert not graph.has_node(
        "navigation"
    )

    assert graph.dependencies_of(
        "home"
    ) == {"footer"}

    assert graph.dependents_of(
        "navigation"
    ) == set()


def test_clear():

    graph = DependencyGraph()

    graph.add_dependency(
        "home",
        "navigation",
    )

    graph.add_dependency(
        "home",
        "footer",
    )

    graph.clear()

    assert graph.nodes == {}


def test_missing_nodes():

    graph = DependencyGraph()

    assert not graph.has_node(
        "does-not-exist"
    )

    assert graph.dependencies_of(
        "does-not-exist"
    ) == set()

    assert graph.dependents_of(
        "does-not-exist"
    ) == set()

    assert graph.affected_by(
        "does-not-exist"
    ) == set()

    assert not graph.transitively_depends_on(
        "does-not-exist",
        "home",
    )


def test_graph_repr():

    graph = DependencyGraph()

    graph.add_dependency(
        "home",
        "navigation",
    )

    output = repr(graph)

    assert "DependencyGraph:" in output
    assert "home" in output
    assert "navigation" in output


if __name__ == "__main__":

    test_add_nodes()
    test_add_dependency()
    test_multiple_dependencies()
    test_self_dependency()
    test_cycle_detection()
    test_affected_by()
    test_direct_dependency()
    test_transitive_dependency()
    test_topological_order()
    test_remove_node()
    test_clear()
    test_missing_nodes()
    test_graph_repr()

    print(
        "All dependency graph tests passed."
    )