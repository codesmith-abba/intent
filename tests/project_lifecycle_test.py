from pathlib import Path
from tempfile import TemporaryDirectory

from itl.project.discovery import ProjectDiscoverer
from itl.project.manager import ProjectManager
from itl.project.models import ProjectState


def test_complete_project_lifecycle():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        manager = ProjectManager()

        state = ProjectState(
            name="SMarket",
            version="1",
            entrypoint="app.itl",
            generator_version="0.1.0",
        )

        # Initialize
        paths = manager.initialize(
            root,
            state,
        )

        assert paths.project.is_dir()
        assert paths.state.is_file()

        # Discover from nested directory
        nested = (
            root
            / "pages"
            / "home"
        )

        nested.mkdir(
            parents=True
        )

        discovered = (
            ProjectDiscoverer().discover(
                nested
            )
        )

        assert discovered == root.resolve()

        # Load
        loaded_paths, loaded_state = (
            manager.load(
                discovered
            )
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

        assert (
            loaded_state.generator_version
            == "0.1.0"
        )

        assert (
            loaded_state.schema_version
            == 1
        )


if __name__ == "__main__":

    test_complete_project_lifecycle()

    print(
        "Complete project lifecycle passed."
    )