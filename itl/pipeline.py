from pathlib import Path

from itl.parser.lexer import Lexer
from itl.parser.parser import Parser
from itl.analyzer.analyzer import Analyzer
from itl.gir.builder import IRBuilder


class Pipeline:

    def compile(self, filename):

        path = Path(filename)

        if path.suffix != ".itl":
            path = path.with_suffix(".itl")

        source = path.read_text(encoding="utf-8")

        tokens = Lexer(source).scan_tokens()

        ast = Parser(tokens).parse()

        Analyzer().analyze(ast)

        ir = IRBuilder().build(ast)

        return ir