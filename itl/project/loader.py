from pathlib import Path

from itl.project.models import ProjectState
from itl.project.paths import ProjectPaths
from itl.project.state import ProjectStateStore


class ProjectLoader:

    def load(
        self,
        root: str | Path,
    ) -> tuple[ProjectPaths, ProjectState]:

        paths = ProjectPaths(root)

        if not paths.project.is_dir():

            raise FileNotFoundError(
                "Project state directory "
                "'.project' does not exist."
            )

        if not paths.state.is_file():

            raise FileNotFoundError(
                "Project state file "
                "'state.json' does not exist."
            )

        state = ProjectStateStore(
            paths.state
        ).load()

        return paths, state