from pathlib import Path

from itl.project.models import ProjectState
from itl.project.paths import ProjectPaths
from itl.project.state import ProjectStateStore


class ProjectInitializer:

    def initialize(
        self,
        root: str | Path,
        state: ProjectState,
    ) -> ProjectPaths:

        paths = ProjectPaths(root)

        paths.project.mkdir(
            parents=True,
            exist_ok=True,
        )

        paths.cache.mkdir(
            parents=True,
            exist_ok=True,
        )

        paths.graph.mkdir(
            parents=True,
            exist_ok=True,
        )

        paths.gir.mkdir(
            parents=True,
            exist_ok=True,
        )

        paths.generation.mkdir(
            parents=True,
            exist_ok=True,
        )

        ProjectStateStore(
            paths.state
        ).save(state)

        return paths