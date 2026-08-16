from pathlib import Path
from tempfile import TemporaryDirectory

from itl.project.manager import ProjectManager
from itl.project.models import ProjectState


def test_initialize_and_load():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        manager = ProjectManager()

        state = ProjectState(
            name="SMarket",
            entrypoint="app.itl",
            generator_version="0.1.0",
        )

        paths = manager.initialize(
            root,
            state,
        )

        assert paths.project.is_dir()
        assert paths.state.is_file()

        loaded_paths, loaded_state = (
            manager.load(root)
        )

        assert (
            loaded_paths.project
            == paths.project
        )

        assert (
            loaded_state.name
            == "SMarket"
        )

        assert (
            loaded_state.entrypoint
            == "app.itl"
        )


def test_manager_loads_existing_project():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        manager = ProjectManager()

        manager.initialize(
            root,
            ProjectState(
                name="TestProject"
            ),
        )

        _, state = manager.load(root)

        assert state.name == "TestProject"


if __name__ == "__main__":

    test_initialize_and_load()
    test_manager_loads_existing_project()

    print(
        "All project manager tests passed."
    )