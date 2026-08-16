from pathlib import Path
from tempfile import TemporaryDirectory

from itl.project.initializer import ProjectInitializer
from itl.project.loader import ProjectLoader
from itl.project.models import ProjectState


def test_load_existing_project():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        state = ProjectState(
            name="SMarket",
            version="2",
            entrypoint="app.itl",
            generator_version="0.1.0",
        )

        ProjectInitializer().initialize(
            root,
            state,
        )

        paths, loaded = ProjectLoader().load(
            root
        )

        assert paths.project.is_dir()

        assert loaded.name == "SMarket"
        assert loaded.version == "2"
        assert loaded.entrypoint == "app.itl"
        assert loaded.schema_version == 1
        assert (
            loaded.generator_version
            == "0.1.0"
        )


def test_missing_project_directory():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        try:

            ProjectLoader().load(root)

        except FileNotFoundError as error:

            assert ".project" in str(error)

        else:

            raise AssertionError(
                "Expected FileNotFoundError"
            )


def test_missing_state_file():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        (root / ".project").mkdir()

        try:

            ProjectLoader().load(root)

        except FileNotFoundError as error:

            assert "state.json" in str(error)

        else:

            raise AssertionError(
                "Expected FileNotFoundError"
            )


if __name__ == "__main__":

    test_load_existing_project()
    test_missing_project_directory()
    test_missing_state_file()

    print(
        "All project loader tests passed."
    )