from pathlib import Path

from itl.explain.explain import Explainer
from itl.ir.builder import IRBuilder
from itl.parser.lexer import Lexer
from itl.parser.parser import Parser

from itl.analyzer.analyzer import Analyzer

source = Path("examples/app.itl").read_text()

tokens = Lexer(source).scan_tokens()

ast = Parser(tokens).parse()

ir = IRBuilder().build(ast)

print(ir)