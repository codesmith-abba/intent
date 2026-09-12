from itl.editor import EditorService, Position
from itl.editor.server import LSPServer


VALID = """app $Store {
    system {
        frontend {
            framework $react
        }
    }

    page $home {
        theme $light
        hero $welcome {
            headline $Welcome
        }
        section $products {
            intent $Featured products
        }
    }
}
"""


def test_syntax_diagnostic_comes_from_lexer():
    service = EditorService()
    diagnostics = service.diagnostics("app.itl", "app Example {}")
    assert len(diagnostics) == 1
    assert "Unknown keyword 'Example'" in diagnostics[0].message


def test_parse_diagnostic_comes_from_parser():
    service = EditorService()
    diagnostics = service.diagnostics("app.itl", "app $Store {")
    assert len(diagnostics) == 1
    assert diagnostics[0].source == "itl"


def test_semantic_diagnostic_comes_from_analyzer():
    service = EditorService()
    source = "app $Store { target $console }"
    diagnostics = service.diagnostics("app.itl", source)
    assert len(diagnostics) == 1
    assert "Unknown target 'console'" in diagnostics[0].message


def test_completion_uses_lexer_keyword_catalog():
    service = EditorService()
    items = service.completions("app $Store { fra", Position(0, 19))
    assert any(item.label == "framework" for item in items)


def test_hover_for_keyword():
    service = EditorService()
    hover = service.hover("app.itl", VALID, Position(1, 4))
    assert hover is not None
    assert "system" in hover.contents


def test_document_symbols_and_definition():
    service = EditorService()
    symbols = service.document_symbols("app.itl", VALID)
    assert symbols[0].name == "Store"
    assert symbols[0].children[0].name == "home"
    assert symbols[0].children[0].children[0].name == "products"

    definition = service.definition("app.itl", VALID, Position(9, 15))
    assert definition is not None
    assert definition.range.start.line == 9


def test_safe_formatting_only_changes_whitespace():
    service = EditorService()
    source = VALID.replace("$Store {", "$Store {  ")[:-1]
    edits = service.format("app.itl", source)
    assert edits
    assert any(edit.new_text.endswith("\n") for edit in edits)


def test_invalid_document_is_not_formatted():
    service = EditorService()
    assert service.format("app.itl", "app $Store { target $bad }") == []


def test_lsp_initialize_and_completion():
    server = LSPServer()
    response = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert response["result"]["capabilities"]["hoverProvider"] is True
    assert response["result"]["capabilities"]["definitionProvider"] is True

    server.handle({
        "jsonrpc": "2.0",
        "method": "textDocument/didOpen",
        "params": {"textDocument": {"uri": "file:///app.itl", "text": "app $Store { target $we"}},
    })
    response = server.handle({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "textDocument/completion",
        "params": {"textDocument": {"uri": "file:///app.itl"}, "position": {"line": 0, "character": 23}},
    })
    labels = {item["label"] for item in response["result"]["items"]}
    assert "web" not in labels
    assert "target" not in labels
