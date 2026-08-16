from itl.project.models import ProjectState


def test_project_state_defaults():

    state = ProjectState(
        name="SMarket"
    )

    assert state.name == "SMarket"
    assert state.version == "1"
    assert state.entrypoint is None
    assert state.generator_version is None


def test_project_state_with_metadata():

    state = ProjectState(
        name="SMarket",
        version="2",
        entrypoint="app.itl",
        generator_version="0.1.0",
    )

    assert state.name == "SMarket"
    assert state.version == "2"
    assert state.entrypoint == "app.itl"
    assert state.generator_version == "0.1.0"


if __name__ == "__main__":

    test_project_state_defaults()
    test_project_state_with_metadata()

    print("All project state tests passed.")