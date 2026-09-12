from __future__ import annotations

from itl.analyzer.analyzer import Analyzer
from itl.analyzer.errors import SemanticError
from itl.parser.ast import App, Page, Section
from itl.parser.errors import ParseError
from itl.parser.lexer import Lexer
from itl.parser.parser import Parser
from itl.parser.source import SourceFile
from itl.parser.token_type import TokenType


def parse(source: str):
    source_file = SourceFile("phase24.itl", source)
    tokens = Lexer(source_file).scan_tokens()
    return Parser(tokens).parse()


def test_lexer_emits_keywords_literals_numbers_and_eof_deterministically():
    source = """// comment
app $Demo {
    page $home {
        intent $(Build a page.)
    }
}
"""

    first = Lexer(SourceFile("phase24.itl", source)).scan_tokens()
    second = Lexer(SourceFile("phase24.itl", source)).scan_tokens()

    assert [(token.type, token.lexeme) for token in first] == [
        (TokenType.APP, "app"),
        (TokenType.STRING, "Demo"),
        (TokenType.LEFT_BRACE, "{"),
        (TokenType.PAGE, "page"),
        (TokenType.STRING, "home"),
        (TokenType.LEFT_BRACE, "{"),
        (TokenType.INTENT, "intent"),
        (TokenType.STRING, "Build a page."),
        (TokenType.RIGHT_BRACE, "}"),
        (TokenType.RIGHT_BRACE, "}"),
        (TokenType.EOF, ""),
    ]
    assert [(token.type, token.lexeme) for token in first] == [
        (token.type, token.lexeme) for token in second
    ]


def test_lexer_preserves_numeric_literals_and_booleans():
    tokens = Lexer(SourceFile("values.itl", "true false 42 3.14")).scan_tokens()

    assert tokens[0].type == TokenType.BOOLEAN
    assert tokens[0].literal is True
    assert tokens[1].type == TokenType.BOOLEAN
    assert tokens[1].literal is False
    assert tokens[2].type == TokenType.NUMBER
    assert tokens[2].literal == 42
    assert tokens[3].type == TokenType.NUMBER
    assert tokens[3].literal == 3.14
    assert tokens[-1].type == TokenType.EOF


def test_lexer_rejects_unknown_keywords_and_unterminated_multiline_literals():
    try:
        Lexer(SourceFile("invalid.itl", "unknown_keyword")).scan_tokens()
    except SyntaxError as error:
        assert "Unknown keyword" in str(error)
    else:
        raise AssertionError("Expected unknown keyword failure")

    try:
        Lexer(SourceFile("invalid.itl", "intent $(missing end")).scan_tokens()
    except SyntaxError as error:
        assert "Unterminated multiline literal" in str(error)
    else:
        raise AssertionError("Expected unterminated multiline literal failure")


def test_parser_builds_expected_ast_shape():
    app = parse(
        """app $Demo {
    page $home {
        hero $welcome {
            headline $Hello
        }
        section $content {
            intent $Content
        }
    }
}
"""
    )

    assert isinstance(app, App)
    assert isinstance(app.pages[0], Page)
    assert isinstance(app.pages[0].sections[0], Section)
    assert app.name == "Demo"
    assert app.pages[0].name == "home"
    assert app.pages[0].hero.name == "welcome"
    assert app.pages[0].hero.headline == "Hello"
    assert app.pages[0].sections[0].intent == "Content"


def test_parser_rejects_unexpected_members_and_missing_braces():
    for source in (
        "app $Demo { page $home { models $x } }",
        "app $Demo { page $home {",
    ):
        try:
            parse(source)
        except ParseError:
            continue
        raise AssertionError("Expected parser failure for invalid structure")


def test_imports_are_preserved_at_application_and_page_levels():
    app = parse(
        """app $Demo {
    import $base
    page $home {
        import $shared
        section $intro {}
    }
}
"""
    )

    assert app.imports == ["base"]
    assert app.pages[0].imports == ["shared"]


def test_semantic_analysis_rejects_duplicate_pages():
    app = parse(
        """app $Demo {
    page $home {}
    page $home {}
}
"""
    )

    try:
        Analyzer().analyze(app)
    except SemanticError:
        return
    raise AssertionError("Expected duplicate page semantic failure")
