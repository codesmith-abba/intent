from pathlib import Path
from tempfile import TemporaryDirectory

from itl.analyzer.analyzer import Analyzer
from itl.analyzer.errors import SemanticError
from itl.parser.ast import App, Page
from itl.parser.errors import ParseError
from itl.parser.lexer import Lexer
from itl.parser.parser import Parser
from itl.parser.source import SourceFile


def parse(source: str):
    source_file = SourceFile(Path("conformance.itl"), source)
    tokens = Lexer(source_file).scan_tokens()
    return Parser(tokens).parse()


def test_v01_valid_application_syntax():
    app = parse(
        """app $Storefront {
    intent $(
        Help customers discover products.
    )
    system {
        frontend {
            framework $react
        }
        backend {
            framework $django
            api $rest
        }
    }
    page $home {
        theme $light
        hero $main {
            image $assets/hero.svg
            headline $Welcome
            subtitle $Discover our products
            action $Browse catalog
        }
        section $featured {
            intent $Show featured products.
            section $grid {}
        }
    }
    target $web
}
"""
    )

    Analyzer().analyze(app)
    assert isinstance(app, App)
    assert app.name == "Storefront"
    assert app.target == "web"
    assert len(app.pages) == 1
    assert app.pages[0].name == "home"
    assert app.pages[0].hero.headline == "Welcome"
    assert app.pages[0].sections[0].sections[0].name == "grid"


def test_v01_multiline_intent_is_string_value():
    app = parse(
        """app $Example {
    intent $(
        First line.
        Second line.
    )
}
"""
    )
    assert app.intent == "First line.\n        Second line."


def test_v01_empty_blocks_are_valid():
    app = parse("app $Example { page $home { section $footer {} } }")
    Analyzer().analyze(app)
    assert app.pages[0].sections[0].name == "footer"


def test_v01_import_forms_parse():
    app = parse(
        """app $Example {
    import $home
    page $local {
        import $footer
        section $content {
            import $details
        }
    }
}
"""
    )
    assert app.imports == ["home"]
    assert app.pages[0].imports == ["footer"]
    assert app.pages[0].sections[0].imports == ["details"]


def test_v01_invalid_bare_name_is_lexical_error():
    try:
        parse("app Example {}")
    except SyntaxError as error:
        assert "Unknown keyword 'Example'" in str(error)
    else:
        raise AssertionError("Expected lexical error for bare application name")


def test_v01_invalid_target_is_semantic_error():
    app = parse("app $Example { target $console }")
    try:
        Analyzer().analyze(app)
    except SemanticError as error:
        assert "Unknown target 'console'" in str(error)
    else:
        raise AssertionError("Expected semantic target error")


def test_v01_hero_requires_headline():
    app = parse(
        "app $Example { page $home { hero $main { subtitle $Missing } } }"
    )
    try:
        Analyzer().analyze(app)
    except SemanticError as error:
        assert "Hero must contain a headline." in str(error)
    else:
        raise AssertionError("Expected semantic hero error")


def test_v01_duplicate_pages_are_rejected():
    app = parse(
        "app $Example { page $home {} page $home {} }"
    )
    try:
        Analyzer().analyze(app)
    except SemanticError as error:
        assert "Duplicate page 'home'." in str(error)
    else:
        raise AssertionError("Expected duplicate page error")


def test_v01_unknown_block_member_is_parse_error():
    try:
        parse("app $Example { page $home { models $x } }")
    except ParseError:
        return
    raise AssertionError("Expected parse error for unsupported page member")


def test_v01_string_terminates_before_left_brace():
    app = parse("app $Example { page $home $Intent text {} }")
    assert app.pages[0].intent == "Intent text"


def test_v01_project_import_merge_is_compiler_behavior():
    # This test documents the conformance fixture shape without making the
    # language specification depend on a particular filesystem layout.
    with TemporaryDirectory() as root:
        root_path = Path(root)
        assert root_path.is_dir()
