from itl.project.models import ProjectState


class ProjectStateValidator:

    def validate(
        self,
        state: ProjectState,
    ) -> None:

        if not state.name.strip():

            raise ValueError(
                "Project name cannot be empty."
            )

        if not state.version.strip():

            raise ValueError(
                "Project version cannot be empty."
            )
        
        if state.schema_version != 1:

            raise ValueError(
                "Unsupported project state schema version."
            )

        if state.entrypoint is not None:

            if not state.entrypoint.strip():

                raise ValueError(
                    "Project entrypoint "
                    "cannot be empty."
                )

        if (
            state.generator_version
            is not None
        ):

            if not state.generator_version.strip():

                raise ValueError(
                    "Generator version "
                    "cannot be empty."
                )