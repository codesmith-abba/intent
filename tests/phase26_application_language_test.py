from pathlib import Path

from itl.analyzer.analyzer import Analyzer
from itl.analyzer.errors import SemanticError
from itl.compiler.loader import ProjectLoader
from itl.gir.builder import GIRBuilder
from itl.parser.ast import App, Model
from itl.parser.errors import ParseError
from itl.parser.lexer import Lexer
from itl.parser.parser import Parser
from itl.parser.source import SourceFile
from itl.parser.token_type import TokenType


def assert_raises(expected, callback):
    try:
        callback()
    except expected:
        return
    raise AssertionError(f"Expected {expected} to be raised")


def test_ecommerce_models_compile_through_gir():
    # The ecommerce example also contains auth.itl, whose authentication
    # grammar is outside Phase 26. Test the Phase 26 model pipeline directly
    # so this acceptance test is isolated from future application modules.
    loader = ProjectLoader(Path("docs/examples/ecommerce"))
    models = loader.load_module("models")
    app = App(intent=None, name="SMarket", imports=[], models=models)

    Analyzer().analyze(app)
    gir = GIRBuilder().build(app)

    assert gir.name == "SMarket"
    assert len(gir.models) >= 10
    assert any(model.name == "Product" for model in gir.models)
    product = next(model for model in gir.models if model.name == "Product")
    assert any(field.name == "price" and field.required for field in product.fields)
    assert any(rel.kind == "belongsTo" and rel.target == "Seller" for rel in product.relationships)


def test_model_keywords_are_lexed_as_reserved_tokens():
    tokens = Lexer(SourceFile("keywords.itl", "models model field type primary required unique readonly nullable default belongsTo hasOne hasMany belongsToMany hasManyThrough create get update delete manage route")).scan_tokens()
    assert tokens[-1].type == TokenType.EOF
    assert all(token.type != TokenType.STRING for token in tokens[:-1])
