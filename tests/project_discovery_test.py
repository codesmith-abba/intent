from pathlib import Path
from tempfile import TemporaryDirectory

from itl.project.discovery import ProjectDiscoverer
from itl.project.initializer import ProjectInitializer
from itl.project.models import ProjectState


def test_discover_from_project_root():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        ProjectInitializer().initialize(
            root,
            ProjectState(
                name="SMarket"
            ),
        )

        discovered = (
            ProjectDiscoverer().discover(root)
        )

        assert discovered == root.resolve()


def test_discover_from_nested_directory():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        ProjectInitializer().initialize(
            root,
            ProjectState(
                name="SMarket"
            ),
        )

        nested = (
            root
            / "pages"
            / "components"
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


def test_discover_from_file():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        ProjectInitializer().initialize(
            root,
            ProjectState(
                name="SMarket"
            ),
        )

        source = root / "app.itl"

        source.write_text(
            "app $SMarket {}",
            encoding="utf-8",
        )

        discovered = (
            ProjectDiscoverer().discover(
                source
            )
        )

        assert discovered == root.resolve()


def test_project_not_found():

    with TemporaryDirectory() as directory:

        start = (
            Path(directory)
            / "some"
            / "nested"
        )

        start.mkdir(
            parents=True
        )

        try:

            ProjectDiscoverer().discover(
                start
            )

        except FileNotFoundError as error:

            assert (
                "Unable to find"
                in str(error)
            )

        else:

            raise AssertionError(
                "Expected FileNotFoundError"
            )


if __name__ == "__main__":

    test_discover_from_project_root()
    test_discover_from_nested_directory()
    test_discover_from_file()
    test_project_not_found()

    print(
        "All project discovery tests passed."
    )