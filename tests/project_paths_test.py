from pathlib import Path

from itl.project.paths import ProjectPaths


def test_project_paths():

    paths = ProjectPaths(
        "/tmp/smarket"
    )

    assert paths.root == Path(
        "/tmp/smarket"
    )

    assert paths.project == Path(
        "/tmp/smarket/.project"
    )

    assert paths.state == Path(
        "/tmp/smarket/.project/state.json"
    )

    assert paths.cache == Path(
        "/tmp/smarket/.project/cache"
    )

    assert paths.graph == Path(
        "/tmp/smarket/.project/graph"
    )

    assert paths.gir == Path(
        "/tmp/smarket/.project/gir"
    )

    assert paths.generation == Path(
        "/tmp/smarket/.project/generation"
    )


def test_project_paths_accept_path():

    root = Path("/tmp/project")

    paths = ProjectPaths(root)

    assert paths.root == root


if __name__ == "__main__":

    test_project_paths()
    test_project_paths_accept_path()

    print("All project paths tests passed.")