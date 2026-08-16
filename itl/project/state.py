import json
from pathlib import Path

from itl.project.errors import ProjectStateError
from itl.project.models import ProjectState
from itl.project.validator import ProjectStateValidator


class ProjectStateStore:

    def __init__(
        self,
        path: str | Path,
    ):

        self.path = Path(path)
        self.validator = ProjectStateValidator()

    def save(
        self,
        state: ProjectState,
    ) -> None:

        self.validator.validate(state)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = {
            "schema_version": state.schema_version,
            "name": state.name,
            "version": state.version,
            "entrypoint": state.entrypoint,
            "generator_version": (
                state.generator_version
            ),
        }

        temporary_path = self.path.with_suffix(
            self.path.suffix + ".tmp"
        )

        temporary_path.write_text(
            json.dumps(
                data,
                indent=2,
            ),
            encoding="utf-8",
        )

        temporary_path.replace(self.path)

    def load(self) -> ProjectState:

        try:

            data = json.loads(
                self.path.read_text(
                    encoding="utf-8"
                )
            )

        except (
            OSError,
            json.JSONDecodeError,
        ) as error:

            raise ProjectStateError(
                f"Unable to read project "
                f"state: {self.path}"
            ) from error

        try:

            state = ProjectState(
                name=data["name"],
                version=data.get(
                    "version",
                    "1",
                ),
                entrypoint=data.get(
                    "entrypoint"
                ),
                generator_version=data.get(
                    "generator_version"
                ),
                schema_version=data.get(
                    "schema_version",
                    1,
                ),
            )

            self.validator.validate(state)

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as error:

            raise ProjectStateError(
                f"Invalid project state: "
                f"{self.path}"
            ) from error

        return state