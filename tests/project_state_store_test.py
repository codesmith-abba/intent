from pathlib import Path
from tempfile import TemporaryDirectory

from itl.project.models import ProjectState
from itl.project.state import ProjectStateStore
from itl.project.errors import ProjectStateError


def test_save_and_load():

    with TemporaryDirectory() as directory:

        path = Path(directory) / "state.json"

        store = ProjectStateStore(path)

        state = ProjectState(
            name="SMarket",
            version="2",
            entrypoint="app.itl",
            generator_version="0.1.0",
        )

        store.save(state)

        assert path.exists()

        loaded = store.load()

        assert loaded.name == "SMarket"
        assert loaded.version == "2"
        assert loaded.entrypoint == "app.itl"
        assert (
            loaded.generator_version
            == "0.1.0"
        )


def test_optional_fields():

    with TemporaryDirectory() as directory:

        path = Path(directory) / "state.json"

        store = ProjectStateStore(path)

        state = ProjectState(
            name="SMarket"
        )

        store.save(state)

        loaded = store.load()

        assert loaded.name == "SMarket"
        assert loaded.version == "1"
        assert loaded.entrypoint is None
        assert loaded.generator_version is None


def test_existing_minimal_state():

    with TemporaryDirectory() as directory:

        path = Path(directory) / "state.json"

        path.write_text(
            '{"name": "SMarket"}',
            encoding="utf-8",
        )

        store = ProjectStateStore(path)

        state = store.load()

        assert state.name == "SMarket"
        assert state.version == "1"
        assert state.schema_version == 1
        assert state.entrypoint is None
        assert state.generator_version is None

def test_save_rejects_invalid_state():

    with TemporaryDirectory() as directory:

        path = Path(directory) / "state.json"

        store = ProjectStateStore(path)

        try:

            store.save(
                ProjectState(
                    name="   "
                )
            )

        except ValueError as error:

            assert "name" in str(error)

        else:

            raise AssertionError(
                "Expected ValueError"
            )


def test_load_rejects_invalid_state():

    with TemporaryDirectory() as directory:

        path = Path(directory) / "state.json"

        path.write_text(
            '{"name": "", "version": "1"}',
            encoding="utf-8",
        )

        store = ProjectStateStore(path)

        try:

            store.load()

        except ProjectStateError as error:

            assert "Invalid project state" in str(error)

        else:

            raise AssertionError(
                "Expected ValueError"
            )

def test_corrupted_state_file():

    with TemporaryDirectory() as directory:

        path = Path(directory) / "state.json"

        path.write_text(
            '{"name": "SMarket"',
            encoding="utf-8",
        )

        store = ProjectStateStore(path)

        try:

            store.load()

        except ProjectStateError as error:

            assert "Unable to read project state" in str(error)

        else:

            raise AssertionError(
                "Expected ProjectStateError"
            )

def test_missing_required_state_field():

    with TemporaryDirectory() as directory:

        path = Path(directory) / "state.json"

        path.write_text(
            '{"version": "1"}',
            encoding="utf-8",
        )

        store = ProjectStateStore(path)

        try:

            store.load()

        except ProjectStateError as error:

            assert "Invalid project state" in str(error)

        else:

            raise AssertionError(
                "Expected ProjectStateError"
            )

def test_save_does_not_leave_temporary_file():

    with TemporaryDirectory() as directory:

        path = Path(directory) / "state.json"

        store = ProjectStateStore(path)

        store.save(
            ProjectState(
                name="SMarket"
            )
        )

        temporary_path = path.with_suffix(
            path.suffix + ".tmp"
        )

        assert path.is_file()
        assert not temporary_path.exists()

if __name__ == "__main__":

    test_save_and_load()
    test_optional_fields()
    test_existing_minimal_state()
    test_save_rejects_invalid_state()
    test_load_rejects_invalid_state()
    test_corrupted_state_file()
    test_missing_required_state_field()
    test_save_does_not_leave_temporary_file()


    print(
        "All project state store tests passed."
    )