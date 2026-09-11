from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


VALID_APP = """app $CLIApp {
    system {
        frontend {
            framework $react
        }
    }
    target $web
}
"""


class CLITest(unittest.TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "itl", *args],
            cwd=cwd,
            text=True,
            capture_output=True,
        )

    def make_project(self, root: Path) -> Path:
        project = root / "project"
        project.mkdir()
        result = self.run_cli("init", str(project))
        self.assertEqual(result.returncode, 0, result.stderr)
        (project / "app.itl").write_text(VALID_APP, encoding="utf-8")
        return project

    def test_valid_project_check(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self.make_project(Path(directory))
            result = self.run_cli("check", str(project))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Check passed", result.stdout)

    def test_invalid_project_has_useful_error(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self.make_project(Path(directory))
            (project / "app.itl").write_text("this is not valid ITL", encoding="utf-8")
            result = self.run_cli("check", str(project))
            self.assertEqual(result.returncode, 1)
            self.assertIn("Check failed", result.stderr)

    def test_missing_project(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli("check", str(Path(directory) / "missing"))
            self.assertEqual(result.returncode, 1)
            self.assertIn("Unable to find an ITL project", result.stderr)

    def test_build_and_incremental_cache_information(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self.make_project(Path(directory))
            first = self.run_cli("build", str(project))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn("Build", first.stdout)
            self.assertTrue((project / ".project" / "app.json").exists())

            second = self.run_cli("plan", str(project))
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("Cache:", second.stdout)

    def test_build_dry_run_does_not_require_output_write(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self.make_project(Path(directory))
            result = self.run_cli("build", "--dry-run", str(project))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Dry run", result.stdout)

    def test_explain(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self.make_project(Path(directory))
            result = self.run_cli("explain", str(project))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_init(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "new-project"
            result = self.run_cli("init", str(project))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project / ".project" / "state.json").exists())

    def test_clean(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self.make_project(Path(directory))
            build = project / ".project" / "build"
            build.mkdir()
            (build / "generated.js").write_text("generated", encoding="utf-8")
            result = self.run_cli("clean", str(project))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(build.exists())

    def test_graph_and_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            project = self.make_project(Path(directory))
            graph = self.run_cli("graph", str(project))
            self.assertEqual(graph.returncode, 0, graph.stderr)
            plan = self.run_cli("plan", str(project))
            self.assertEqual(plan.returncode, 0, plan.stderr)
            self.assertIn("Action:", plan.stdout)

    def test_usage_error_has_nonzero_exit_code(self):
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage:", result.stderr)


if __name__ == "__main__":
    unittest.main()
