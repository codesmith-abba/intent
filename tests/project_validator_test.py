from itl.project.models import ProjectState
from itl.project.validator import ProjectStateValidator


def test_valid_state():

    state = ProjectState(
        name="SMarket",
        version="1",
        entrypoint="app.itl",
        generator_version="0.1.0",
    )

    ProjectStateValidator().validate(
        state
    )


def test_empty_name():

    state = ProjectState(
        name="   "
    )

    try:

        ProjectStateValidator().validate(
            state
        )

    except ValueError as error:

        assert "name" in str(error)

    else:

        raise AssertionError(
            "Expected ValueError"
        )


def test_empty_version():

    state = ProjectState(
        name="SMarket",
        version="   ",
    )

    try:

        ProjectStateValidator().validate(
            state
        )

    except ValueError as error:

        assert "version" in str(error)

    else:

        raise AssertionError(
            "Expected ValueError"
        )


def test_empty_entrypoint():

    state = ProjectState(
        name="SMarket",
        entrypoint="   ",
    )

    try:

        ProjectStateValidator().validate(
            state
        )

    except ValueError as error:

        assert "entrypoint" in str(error)

    else:

        raise AssertionError(
            "Expected ValueError"
        )


def test_empty_generator_version():

    state = ProjectState(
        name="SMarket",
        generator_version="   ",
    )

    try:

        ProjectStateValidator().validate(
            state
        )

    except ValueError as error:

        assert "Generator version" in str(error)

    else:

        raise AssertionError(
            "Expected ValueError"
        )

def test_unsupported_schema_version():

    state = ProjectState(
        name="SMarket",
        schema_version=999,
    )

    try:

        ProjectStateValidator().validate(
            state
        )

    except ValueError as error:

        assert "schema version" in str(error)

    else:

        raise AssertionError(
            "Expected ValueError"
        )


if __name__ == "__main__":

    test_valid_state()
    test_empty_name()
    test_empty_version()
    test_empty_entrypoint()
    test_empty_generator_version()

    print(
        "All project validator tests passed."
    )