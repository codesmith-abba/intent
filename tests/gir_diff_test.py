from itl.gir.diff import GIRDiffAnalyzer, GIRDiffCategory
from itl.gir.models import GIRHero, GIRPage, GIRSection, GIRSystem


def test_style_change_is_classified():
    previous = {"page": GIRPage(None, "page", theme="light")}
    current = {"page": GIRPage(None, "page", theme="dark")}

    diff = GIRDiffAnalyzer.analyze(previous, current)

    assert diff.nodes[0].categories == (GIRDiffCategory.STYLE,)
    assert diff.nodes[0].fields[0].path == "theme"


def test_layout_change_is_classified():
    previous = {"page": GIRPage(None, "page", components=[])}
    current = {
        "page": GIRPage(
            None,
            "page",
            components=[GIRHero(None, "hero")],
        )
    }

    diff = GIRDiffAnalyzer.analyze(previous, current)

    assert GIRDiffCategory.LAYOUT in diff.nodes[0].categories
    assert GIRDiffCategory.STRUCTURAL in diff.nodes[0].categories


def test_content_change_is_classified():
    previous = {"hero": GIRHero(None, "hero", headline="Old")}
    current = {"hero": GIRHero(None, "hero", headline="New")}

    diff = GIRDiffAnalyzer.analyze(previous, current)

    assert diff.nodes[0].categories == (GIRDiffCategory.CONTENT,)


def test_logic_change_is_classified():
    previous = {"hero": GIRHero(None, "hero", action="open")}
    current = {"hero": GIRHero(None, "hero", action="submit")}

    diff = GIRDiffAnalyzer.analyze(previous, current)

    assert diff.nodes[0].categories == (GIRDiffCategory.LOGIC,)


def test_architecture_change_is_classified():
    previous = {"system": GIRSystem(None, backend="old-api")}
    current = {"system": GIRSystem(None, backend="new-api")}

    diff = GIRDiffAnalyzer.analyze(previous, current)

    assert diff.nodes[0].categories == (GIRDiffCategory.ARCHITECTURE,)


def test_dependency_change_is_architectural_and_structural():
    node = GIRPage(None, "page")
    diff = GIRDiffAnalyzer.analyze(
        {"page": node},
        {"page": node},
        previous_dependencies={"page": {"a"}},
        current_dependencies={"page": {"b"}},
    )

    assert diff.nodes[0].categories == (
        GIRDiffCategory.ARCHITECTURE,
        GIRDiffCategory.STRUCTURAL,
    )
    assert diff.nodes[0].fields[-1].path == "dependencies"


def test_multiple_change_categories_are_reported_together():
    previous = {
        "hero": GIRHero(
            None,
            "hero",
            headline="Old",
            action="open",
        )
    }
    current = {
        "hero": GIRHero(
            None,
            "hero",
            headline="New",
            action="submit",
        )
    }

    diff = GIRDiffAnalyzer.analyze(previous, current)

    assert diff.nodes[0].categories == (
        GIRDiffCategory.CONTENT,
        GIRDiffCategory.LOGIC,
    )
    assert [field.path for field in diff.nodes[0].fields] == [
        "action",
        "headline",
    ]


def test_added_and_removed_nodes_are_structural():
    added = GIRDiffAnalyzer.analyze(
        {},
        {"hero": GIRHero(None, "hero")},
    )
    removed = GIRDiffAnalyzer.analyze(
        {"hero": GIRHero(None, "hero")},
        {},
    )

    assert added.nodes[0].categories == (GIRDiffCategory.STRUCTURAL,)
    assert removed.nodes[0].categories == (GIRDiffCategory.STRUCTURAL,)
    assert added.nodes[0].previous_type is None
    assert removed.nodes[0].current_type is None


def test_node_type_change_is_structural():
    diff = GIRDiffAnalyzer.analyze(
        {"node": GIRHero(None, "node")},
        {"node": GIRSection(None, "node")},
    )

    assert diff.nodes[0].categories == (GIRDiffCategory.STRUCTURAL,)
    assert diff.nodes[0].previous_type == "GIRHero"
    assert diff.nodes[0].current_type == "GIRSection"


def test_unchanged_nodes_are_not_changed():
    node = GIRPage(None, "page", theme="light")
    diff = GIRDiffAnalyzer.analyze(
        {"page": node},
        {"page": GIRPage(None, "page", theme="light")},
    )

    assert diff.changed == ()
    assert [item.node_id for item in diff.unchanged] == ["page"]


def test_results_are_deterministic():
    previous = {
        "z": GIRHero(None, "z", headline="old"),
        "a": GIRHero(None, "a", action="open"),
    }
    current = {
        "a": GIRHero(None, "a", action="submit"),
        "z": GIRHero(None, "z", headline="new"),
    }

    first = GIRDiffAnalyzer.analyze(previous, current)
    second = GIRDiffAnalyzer.analyze(previous, current)

    assert first == second
    assert [item.node_id for item in first.nodes] == ["a", "z"]


if __name__ == "__main__":
    test_style_change_is_classified()
    test_layout_change_is_classified()
    test_content_change_is_classified()
    test_logic_change_is_classified()
    test_architecture_change_is_classified()
    test_dependency_change_is_architectural_and_structural()
    test_multiple_change_categories_are_reported_together()
    test_added_and_removed_nodes_are_structural()
    test_node_type_change_is_structural()
    test_unchanged_nodes_are_not_changed()
    test_results_are_deterministic()
    print("All GIR diff tests passed.")
