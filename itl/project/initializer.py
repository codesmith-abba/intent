from pathlib import Path

from itl.project.models import ProjectState
from itl.project.paths import ProjectPaths
from itl.project.state import ProjectStateStore


DEFAULT_APP_TEMPLATE = """app $__PROJECT_NAME__ {

    target $web

    framework $react
}
"""


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

        entrypoint = root / (state.entrypoint or "app.itl")
        if not entrypoint.exists():
            entrypoint.write_text(
                DEFAULT_APP_TEMPLATE.replace("$__PROJECT_NAME__", f"${state.name}"),
                encoding="utf-8",
            )

        return paths
