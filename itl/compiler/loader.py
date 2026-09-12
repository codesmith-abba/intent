from pathlib import Path

from itl.parser.lexer import Lexer
from itl.parser.parser import Parser
from itl.parser.source import SourceFile
from itl.security import SecurityError, ensure_within, safe_relative_path


class ProjectLoader:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def load_app(self, filename: str = "app.itl"):
        return self.parse_file(filename)

    def load_module(self, name: str):
        return self.parse_file(f"{name}.itl", module=True)

    def list_modules(self) -> list[str]:
        return sorted(
            path.stem
            for path in self.root.glob("*.itl")
            if path.name != "app.itl" and path.is_file()
        )

    def parse_file(self, filename: str, module: bool = False):
        source = self.load_file(filename)
        tokens = Lexer(source).scan_tokens()
        parser = Parser(tokens)
        return parser.parse_module() if module else parser.parse()

    def load_file(self, filename: str):
        relative = safe_relative_path(filename)
        if not relative.endswith(".itl"):
            raise SecurityError("ITL source imports must target .itl files.")
        path = ensure_within(self.root, self.root / relative)
        if not path.is_file():
            raise FileNotFoundError(path)
        return SourceFile(path=path, text=path.read_text(encoding="utf-8"))
