from pathlib import Path

from itl.parser.lexer import Lexer
from itl.parser.parser import Parser


class ProjectLoader:

    def __init__(self, root: str | Path):
        self.root = Path(root)

    def load_app(self, filename: str = "app.itl"):
        return self.parse_file(filename)

    def load_module(self, name: str):
        return self.parse_file(f"{name}.itl", module=True)

    def parse_file(
        self,
        filename: str,
        module: bool = False,
    ):
        tokens = self.load_file(filename)

        parser = Parser(tokens)

        if module:
            return parser.parse_module()

        return parser.parse()

    def load_file(self, filename: str):
        path = self.root / filename

        source = path.read_text(encoding="utf-8")

        return Lexer(source).scan_tokens()