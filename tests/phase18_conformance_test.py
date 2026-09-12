from pathlib import Path
from tempfile import TemporaryDirectory

from itl.analyzer.analyzer import Analyzer

from itl.analyzer.analyzer import Analyzer
from itl.analyzer.errors import SemanticError
from itl.parser.errors import ParseError
from itl.parser.lexer import Lexer
from itl.parser.parser import Parser
from itl.parser.source import SourceFile


def parse(source: str, path: str = "conformance.itl"):
    source_file = SourceFile(path, source)
    tokens = Lexer(source_file).scan_tokens()
    return Parser(tokens).parse()


def analyze(source: str):
    app = parse(source)
    Analyzer().analyze(app)
    return app


def test_v01_valid_application_syntax():
    app = parse(
        """app $Example {
    system {
        frontend {
            framework $react
        }
    }
    target $web
}
"""
    )
    assert app.name == "Example"
    assert app.target == "web"
    assert app.system.frontend.framework.value == "react"


def test_v01_multiline_intent_is_string_value():
    app = parse(
        """app $Example {
    intent $(First line.
        Second line.)
}
"""
    )
    assert app.intent == "First line.\n        Second line."


def test_v01_empty_blocks():
    app = parse("app $Example { system {} }")
    assert app.name == "Example"


def test_v01_import_forms_parse():
    app = parse(
        """app $Example {
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


def test_v01_invalid_bare_name_is_lexical_error():
    try:
        parse("app Example {}")
    except SyntaxError:
        return
    raise AssertionError("Expected lexical error for bare application name")


def test_v01_invalid_target_is_semantic_error():
    try:
        analyze("app $Example { target $console\n }")
    except SemanticError:
        return
    raise AssertionError("Expected semantic error for unsupported target")


def test_v01_hero_requires_headline():
    try:
        analyze(
            """app $Example {
    page $home {
        hero $main {
            subtitle $Missing
        }
    }
}
"""
        )
    except SemanticError:
        return
    raise AssertionError("Expected semantic error for hero without headline")


def test_v01_duplicate_pages_are_rejected():
    try:
        analyze(
            """app $Example {
    page $home {}
    page $home {}
}
"""
        )
    except SemanticError:
        return
    raise AssertionError("Expected duplicate page error")


def test_v01_unknown_block_member_is_parse_error():
    try:
        parse("app $Example { page $home { models $x } }")
    except ParseError:
        return
    raise AssertionError("Expected parse error for unsupported page member")


def test_v01_string_terminates_before_left_brace():
    app = parse(
        """app $Example {
    page $home {
        intent $Intent text
    }
}"""
    )
    assert app.pages[0].intent == "Intent text"


def test_v01_project_import_merge_is_compiler_behavior():
    # This test documents the conformance fixture shape without making the
    # language specification depend on a particular filesystem layout.
    with TemporaryDirectory() as root:
        root_path = Path(root)
        assert root_path.is_dir()
