from __future__ import annotations

import os
import tempfile
from pathlib import Path

from itl.backend.react import ReactBackend
from itl.cli import CLI
from itl.cli_service import ProjectService
from itl.gir.models import GIRHero, GIRPage, GIRSection


def test_project_commands_default_to_current_directory():
    parser = CLI().parser()

    for command_name in ("check", "build", "dev", "explain", "clean", "graph", "plan"):
        args = parser.parse_args([command_name])
        assert args.project == "."


def test_dev_starts_server_by_default():
    args = CLI().parser().parse_args(["dev"])
    assert args.run is True


def test_dev_can_skip_server_start():
    args = CLI().parser().parse_args(["dev", "--no-run"])
    assert args.run is False


def test_dev_defaults_to_current_directory():
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        ProjectService().init(project)
        previous = Path.cwd()
        try:
            os.chdir(project)
            assert CLI().run(["dev", "--no-run"]) == 0
            browser = project / ".project" / "build" / "browser"
            assert (browser / "browser.js").exists()
            assert (browser / "runtime.json").exists()
            assert (browser / "index.html").exists()
        finally:
            os.chdir(previous)


def test_react_backend_renders_gir_components():
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        page = GIRPage(
            name="home",
            intent=None,
            components=[
                GIRHero(
                    name="main",
                    intent=None,
                    headline="Welcome",
                    subtitle="Build with intention",
                    action="Learn more",
                ),
                GIRSection(
                    name="featured",
                    intent=None,
                    children=[GIRSection(name="nested", intent=None)],
                ),
            ],
        )

        class Project:
            pages = [page]

        ReactBackend().generate(Project(), output)
        generated = (output / "react" / "src" / "pages" / "home.tsx").read_text(encoding="utf-8")

        assert "Welcome" in generated
        assert "Build with intention" in generated
        assert "Learn more" in generated
        assert "Featured" in generated
        assert "Nested" in generated


def test_react_backend_renders_empty_page_without_legacy_attributes():
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        page = GIRPage(name="home", intent=None)

        class Project:
            pages = [page]

        ReactBackend().generate(Project(), output)
        generated = (output / "react" / "src" / "pages" / "home.tsx").read_text(encoding="utf-8")

        assert "<main>" in generated
        assert "{self.render_hero" not in generated
