import argparse
from pathlib import Path

from itl.gir.writer import IRWriter
from itl.explain.explain import Explainer
from itl.backend.react import ReactBackend

from itl.pipeline import Pipeline


class CLI:

    def run(self):

        parser = argparse.ArgumentParser(
            prog="itl",
            description="Intent Language CLI"
        )

        subparsers = parser.add_subparsers(
            dest="command",
            required=True
        )

        # explain
        explain = subparsers.add_parser(
            "explain",
            help="Explain an ITL application"
        )

        explain.add_argument(
            "file",
            help="Path to .itl file"
        )

        # Build
        build = subparsers.add_parser(
            "build",
            help="Build the .itl project"
        )

        build.add_argument(
            "file",
            help="Path to .itl file"
        )

        dev = subparsers.add_parser(
            "dev",
            help="Generate a React project"
        )

        dev.add_argument("file")

        args = parser.parse_args()

        if args.command == "explain":
            self.explain(args.file)
        elif args.command == "build":
            self.build(args.file)
        elif args.command == "dev":
            self.dev(args.file)

    def explain(self, filename):

        ir = Pipeline().compile(filename)

        Explainer().explain(ir)
    
    def build(self, filename):

        ir = Pipeline().compile(filename)

        IRWriter().write(ir)

        print("✓ Build completed.")
    
    def dev(self, filename):

        print("Compiling...")

        project = Pipeline().compile(filename)

        ReactBackend().generate(project, Path(".project") / "build")

        print("✓ Development server started.")