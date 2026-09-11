from __future__ import annotations

import argparse
import sys
from pathlib import Path

from itl.cli_service import CLIServiceError, ProjectService


EXIT_OK = 0
EXIT_USAGE = 2
EXIT_FAILURE = 1


class CLI:
    """Thin command-line interface over compiler/project services."""

    def __init__(self, service: ProjectService | None = None) -> None:
        self.service = service or ProjectService()

    def parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="itl",
            description="Intent Language compiler CLI",
        )
        subparsers = parser.add_subparsers(dest="command", required=True)

        def project_command(name: str, help_text: str):
            command = subparsers.add_parser(name, help=help_text)
            command.add_argument("project", help="Project directory or a path inside it")
            return command

        project_command("explain", "Explain an ITL project")
        build = project_command("build", "Build an ITL project")
        build.add_argument("--dry-run", action="store_true", help="Report build actions without writing output")
        project_command("dev", "Generate a development build")
        project_command("check", "Validate an ITL project")
        project_command("clean", "Remove generated development output")
        project_command("graph", "Show the persisted project graph")
        project_command("plan", "Show the current build/cache plan")
        init = subparsers.add_parser("init", help="Initialize an ITL project")
        init.add_argument("project", help="Directory to initialize")

        return parser

    def run(self, argv: list[str] | None = None) -> int:
        parser = self.parser()
        args = parser.parse_args(argv)

        try:
            if args.command == "init":
                project = self.service.init(args.project)
                print(f"Initialized ITL project: {project}")
                return EXIT_OK

            if args.command == "check":
                project, _ = self.service.check(args.project)
                print(f"✓ Check passed: {project}")
                return EXIT_OK

            if args.command == "explain":
                self.service.explain(args.project)
                return EXIT_OK

            if args.command == "build":
                result = self.service.build(args.project, dry_run=args.dry_run)
                prefix = "Dry run" if args.dry_run else "Build"
                print(f"{prefix}: {result['project']}")
                print(f"  status: {result['status']}")
                print(f"  cache: {result['cache_status']} — {result['cache_reason']}")
                if not args.dry_run:
                    print(f"  output: {result['output']}")
                return EXIT_OK

            if args.command == "dev":
                project = self.service.dev(args.project)
                print(f"✓ Development build completed: {project}")
                print(f"  output: {project / '.project' / 'build'}")
                return EXIT_OK

            if args.command == "clean":
                path = self.service.clean(args.project)
                print(f"✓ Cleaned: {path}")
                return EXIT_OK

            if args.command == "graph":
                print(self.service.graph(args.project))
                return EXIT_OK

            if args.command == "plan":
                result = self.service.plan(args.project)
                print(f"Project: {result['project']}")
                print(f"Entrypoint: {result['entrypoint']}")
                print(f"Action: {result['action']}")
                print(f"Cache: {result['cache_status']} — {result['reason']}")
                return EXIT_OK

            parser.error(f"Unknown command: {args.command}")
            return EXIT_USAGE

        except CLIServiceError as error:
            print(f"itl: error: {error}", file=sys.stderr)
            return EXIT_FAILURE
        except KeyboardInterrupt:
            print("itl: interrupted", file=sys.stderr)
            return 130

    # Backward-compatible method surface for callers that used CLI directly.
    def explain(self, filename: str | Path) -> None:
        self.service.explain(filename)

    def build(self, filename: str | Path) -> None:
        result = self.service.build(filename)
        print(f"✓ Build completed: {result['project']}")

    def dev(self, filename: str | Path) -> None:
        project = self.service.dev(filename)
        print(f"✓ Development build completed: {project}")


def main(argv: list[str] | None = None) -> int:
    return CLI().run(argv)
