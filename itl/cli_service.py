from __future__ import annotations

import json
import shutil
from pathlib import Path

from itl.backend.react import ReactBackend
from itl.cache.cache import Cache
from itl.cache.decider import CacheDecider
from itl.cache.decision import CacheStatus
from itl.compiler.compiler import Compiler
from itl.explain.explain import Explainer
from itl.gir.writer import IRWriter
from itl.graph.graph import DependencyGraph
from itl.pipeline import Pipeline
from itl.project.discovery import ProjectDiscoverer
from itl.project.initializer import ProjectInitializer
from itl.project.models import ProjectState
from itl.project.paths import ProjectPaths


class CLIServiceError(Exception):
    """A user-facing CLI service error."""


class ProjectService:
    """Thin application service used by CLI commands.

    Command handlers should only parse arguments, call this service, and
    format the returned information. Compiler/build policy stays here or in
    the existing compiler/build modules.
    """

    def __init__(self) -> None:
        self.discoverer = ProjectDiscoverer()

    def discover(self, path: str | Path) -> Path:
        try:
            return self.discoverer.discover(path)
        except FileNotFoundError as error:
            raise CLIServiceError(
                f"Unable to find an ITL project from '{path}'. "
                "Run 'itl init <project>' to create one."
            ) from error

    def app_file(self, project: Path) -> Path:
        entrypoint = project / "app.itl"
        if not entrypoint.is_file():
            raise CLIServiceError(
                f"Project '{project}' has no app.itl entrypoint."
            )
        return entrypoint

    def check(self, path: str | Path):
        project = self.discover(path)
        try:
            # Use the project compiler for project-level validation.
            return project, Compiler(project).compile()
        except Exception as error:
            raise CLIServiceError(
                f"Check failed for '{project}': {error}"
            ) from error

    def explain(self, path: str | Path):
        project = self.discover(path)
        try:
            # Keep the existing human-readable explainer contract.
            ir = Pipeline().compile(self.app_file(project))
            return project, Explainer().explain(ir)
        except Exception as error:
            raise CLIServiceError(
                f"Unable to explain '{project}': {error}"
            ) from error

    def build(self, path: str | Path, *, dry_run: bool = False):
        project = self.discover(path)
        entrypoint = self.app_file(project)

        cache = Cache(ProjectPaths(project).cache)
        decision = CacheDecider(cache).decide(str(entrypoint))

        try:
            ir = Pipeline().compile(entrypoint)
        except Exception as error:
            raise CLIServiceError(
                f"Build failed for '{project}': {error}"
            ) from error

        if dry_run:
            return {
                "project": project,
                "status": "dry-run",
                "cache_status": decision.status.value,
                "cache_reason": decision.reason,
                "entrypoint": entrypoint,
            }

        try:
            IRWriter().write(ir)
        except Exception as error:
            raise CLIServiceError(
                f"Build output failed for '{project}': {error}"
            ) from error

        cache.put(
            str(entrypoint),
            output=str(project / ".project" / "app.json"),
            metadata={"status": "success"},
        )
        cache.save()

        return {
            "project": project,
            "status": "success",
            "cache_status": decision.status.value,
            "cache_reason": decision.reason,
            "entrypoint": entrypoint,
            "output": project / ".project" / "app.json",
        }

    def dev(self, path: str | Path):
        project = self.discover(path)
        entrypoint = self.app_file(project)
        try:
            compiled = Pipeline().compile(entrypoint)
            ReactBackend().generate(compiled, project / ".project" / "build")
        except Exception as error:
            raise CLIServiceError(
                f"Development build failed for '{project}': {error}"
            ) from error
        return project

    def graph(self, path: str | Path) -> str:
        project = self.discover(path)
        # The persisted graph is compiler state when present. Do not invent a
        # second dependency model in the CLI.
        graph_file = ProjectPaths(project).graph / "graph.json"
        if graph_file.is_file():
            try:
                data = json.loads(graph_file.read_text(encoding="utf-8"))
                return json.dumps(data, indent=2, sort_keys=True)
            except (OSError, json.JSONDecodeError) as error:
                raise CLIServiceError(
                    f"Unable to read project graph: {graph_file}"
                ) from error

        return repr(DependencyGraph())

    def plan(self, path: str | Path) -> dict[str, object]:
        project = self.discover(path)
        entrypoint = self.app_file(project)
        cache = Cache(ProjectPaths(project).cache)
        decision = CacheDecider(cache).decide(str(entrypoint))
        action = "build" if decision.status is not CacheStatus.HIT else "cached"
        return {
            "project": project,
            "entrypoint": entrypoint,
            "action": action,
            "cache_status": decision.status.value,
            "reason": decision.reason,
        }

    def clean(self, path: str | Path) -> Path:
        project = self.discover(path)
        build_root = project / ".project" / "build"
        if build_root.exists():
            shutil.rmtree(build_root)
        return build_root

    def init(self, path: str | Path) -> Path:
        root = Path(path).expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)
        paths = ProjectInitializer().initialize(
            root,
            ProjectState(name=root.name, entrypoint="app.itl"),
        )
        return paths.project
