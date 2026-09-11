from pathlib import Path
from tempfile import TemporaryDirectory

from itl.gir.changes import GIRChangeDetector, GIRChangeType
from itl.gir.invalidation import GIRDependencyInvalidator
from itl.gir.store import GIRFingerprintStore, IncrementalStateError
from itl.graph.graph import DependencyGraph


def test_fingerprint_store_round_trips_deterministically():
    with TemporaryDirectory() as directory:
        path = Path(directory) / ".project" / "gir" / "fingerprints.json"
        store = GIRFingerprintStore(path)
        values = {"b": "2", "a": "1"}

        store.save(values)

        assert store.load() == values
        assert path.read_text(encoding="utf-8") == (
            '{\n  "a": "1",\n  "b": "2"\n}\n'
        )


def test_missing_fingerprint_state_is_empty():
    with TemporaryDirectory() as directory:
        store = GIRFingerprintStore(Path(directory) / "fingerprints.json")
        assert store.load() == {}


def test_corrupt_fingerprint_state_is_rejected():
    with TemporaryDirectory() as directory:
        path = Path(directory) / "fingerprints.json"
        path.write_text("not json", encoding="utf-8")

        try:
            GIRFingerprintStore(path).load()
        except IncrementalStateError:
            pass
        else:
            raise AssertionError("Expected corrupt state to raise IncrementalStateError")


def test_change_detector_classifies_all_change_types():
    changes = GIRChangeDetector.detect(
        {"unchanged": "same", "modified": "old", "removed": "gone"},
        {"unchanged": "same", "modified": "new", "added": "new"},
    )

    assert [(item.node_id, item.change_type) for item in changes.changes] == [
        ("added", GIRChangeType.ADDED),
        ("modified", GIRChangeType.MODIFIED),
        ("removed", GIRChangeType.REMOVED),
        ("unchanged", GIRChangeType.UNCHANGED),
    ]


def test_gir_invalidation_uses_existing_graph_transitively():
    graph = DependencyGraph()
    graph.add_dependency("b", "a")
    graph.add_dependency("c", "b")
    graph.add_node("independent")

    changes = GIRChangeDetector.detect(
        {"a": "old", "b": "same", "c": "same", "independent": "same"},
        {"a": "new", "b": "same", "c": "same", "independent": "same"},
    )

    affected = GIRDependencyInvalidator(graph).affected_nodes(changes)

    assert affected == {"a", "b", "c"}
    assert "independent" not in affected


def test_removed_node_can_invalidate_previous_dependents():
    graph = DependencyGraph()
    graph.add_node("remaining")

    changes = GIRChangeDetector.detect(
        {"removed": "old", "remaining": "same"},
        {"remaining": "same"},
    )

    affected = GIRDependencyInvalidator(graph).affected_nodes(
        changes,
        previous_dependents={"removed": {"remaining"}},
    )

    assert affected == {"remaining"}


if __name__ == "__main__":
    test_fingerprint_store_round_trips_deterministically()
    test_missing_fingerprint_state_is_empty()
    test_corrupt_fingerprint_state_is_rejected()
    test_change_detector_classifies_all_change_types()
    test_gir_invalidation_uses_existing_graph_transitively()
    test_removed_node_can_invalidate_previous_dependents()
    print("All GIR incremental tests passed.")
