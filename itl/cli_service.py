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
    """Thin application service used by CLI commands."""

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
            return project, Compiler(project).compile()
        except Exception as error:
            raise CLIServiceError(
                f"Check failed for '{project}': {error}"
            ) from error

    def explain(self, path: str | Path):
        project = self.discover(path)
        try:
            ir = Pipeline().compile(self.app_file(project))
            return project, Explainer().explain(ir)
        except Exception as error:
            raise CLIServiceError(
                f"Unable to explain '{project}': {error}"
            ) from error

    def build(self, path: str | Path, *, dry_run: bool = False):
        project = self.discover(path)
        entrypoint = self.app_file(project)
        paths = ProjectPaths(project)
        cache = Cache(paths.cache)
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

        output_root = paths.project
        try:
            IRWriter(output_root).write(ir)
        except Exception as error:
            raise CLIServiceError(
                f"Build output failed for '{project}': {error}"
            ) from error

        cache.put(
            str(entrypoint),
            output=str(output_root / "app.json"),
            metadata={"status": "success"},
        )
        cache.save()

        return {
            "project": project,
            "status": "success",
            "cache_status": decision.status.value,
            "cache_reason": decision.reason,
            "entrypoint": entrypoint,
            "output": output_root / "app.json",
        }

    def dev(self, path: str | Path):
        project = self.discover(path)
        entrypoint = self.app_file(project)
        try:
            compiled = Pipeline().compile(entrypoint)
            build_root = project / ".project" / "build"
            ReactBackend().generate(compiled, build_root)
            IRWriter(project / ".project").write(compiled)

            browser_root = build_root / "browser"
            browser_root.mkdir(parents=True, exist_ok=True)
            shutil.copy2(Path(__file__).resolve().parents[1] / "runtime" / "browser.js", browser_root / "browser.js")
            shutil.copy2(project / ".project" / "runtime.json", browser_root / "runtime.json")
            (browser_root / "index.html").write_text(
                "<!doctype html>\n"
                '<html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                "<title>ITL Development Runtime</title></head>\n"
                '<body><div id="app"></div>\n'
                '<script src="./browser.js"></script>\n'
                "<script>new ITLBrowserRuntime.BrowserRuntime({"
                "root: document.getElementById('app')"
                "}).start('./runtime.json');</script>\n"
                "</body></html>\n",
                encoding="utf-8",
            )
        except Exception as error:
            raise CLIServiceError(
                f"Development build failed for '{project}': {error}"
            ) from error
        return project

    def graph(self, path: str | Path) -> str:
        project = self.discover(path)
        paths = ProjectPaths(project)
        candidates = (
            paths.graph / "graph.json",
            paths.project / "graph.json",
        )
        graph_file = next((candidate for candidate in candidates if candidate.is_file()), None)
        if graph_file is not None:
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
