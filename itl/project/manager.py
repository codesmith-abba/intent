from pathlib import Path

from itl.project.initializer import ProjectInitializer
from itl.project.loader import ProjectLoader
from itl.project.models import ProjectState
from itl.project.paths import ProjectPaths


class ProjectManager:

    def __init__(self):

        self.initializer = ProjectInitializer()
        self.loader = ProjectLoader()

    def initialize(
        self,
        root: str | Path,
        state: ProjectState,
    ) -> ProjectPaths:

        return self.initializer.initialize(
            root,
            state,
        )

    def load(
        self,
        root: str | Path,
    ) -> tuple[ProjectPaths, ProjectState]:

        return self.loader.load(root)