from pathlib import Path
from tempfile import TemporaryDirectory

from itl.project.initializer import ProjectInitializer
from itl.project.models import ProjectState
from itl.project.state import ProjectStateStore


def test_initialize_project():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        state = ProjectState(
            name="SMarket",
            entrypoint="app.itl",
            generator_version="0.1.0",
        )

        paths = ProjectInitializer().initialize(
            root,
            state,
        )

        assert paths.project.is_dir()
        assert paths.cache.is_dir()
        assert paths.graph.is_dir()
        assert paths.gir.is_dir()
        assert paths.generation.is_dir()

        assert paths.state.is_file()

        loaded = ProjectStateStore(
            paths.state
        ).load()

        assert loaded.name == "SMarket"
        assert loaded.entrypoint == "app.itl"
        assert (
            loaded.generator_version
            == "0.1.0"
        )


def test_initialize_is_idempotent():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        state = ProjectState(
            name="SMarket"
        )

        initializer = ProjectInitializer()

        first = initializer.initialize(
            root,
            state,
        )

        second = initializer.initialize(
            root,
            state,
        )

        assert first.project == second.project
        assert first.state == second.state
        assert first.cache == second.cache


if __name__ == "__main__":

    test_initialize_project()
    test_initialize_is_idempotent()

    print(
        "All project initializer tests passed."
    )