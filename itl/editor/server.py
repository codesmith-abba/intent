from __future__ import annotations

import json
import sys
from typing import Any

from .models import Position
from .service import EditorService


class LSPServer:
    """Small dependency-free JSON-RPC/LSP adapter over EditorService."""

    def __init__(self, service: EditorService | None = None):
        self.service = service or EditorService()
        self.documents: dict[str, str] = {}

    def handle(self, message: dict[str, Any]) -> dict[str, Any] | None:
        method = message.get("method")
        request_id = message.get("id")
        params = message.get("params") or {}

        if method == "initialize":
            return self._response(
                request_id,
                {
                    "capabilities": {
                        "textDocumentSync": 1,
                        "completionProvider": {"triggerCharacters": ["$"]},
                        "hoverProvider": True,
                        "definitionProvider": True,
                        "documentSymbolProvider": True,
                        "documentFormattingProvider": True,
                    },
                    "serverInfo": {"name": "itl-language-server", "version": "0.1"},
                },
            )

        if method == "shutdown":
            return self._response(request_id, None)

        if method == "exit":
            return None

        if method == "textDocument/didOpen":
            document = params["textDocument"]
            self.documents[document["uri"]] = document["text"]
            return None

        if method == "textDocument/didChange":
            document = params["textDocument"]
            changes = params.get("contentChanges", [])
            if changes and "text" in changes[-1]:
                self.documents[document["uri"]] = changes[-1]["text"]
            return None

        if method == "textDocument/diagnostic":
            uri, text = self._document(params)
            return self._response(request_id, {"items": [self._diagnostic(d) for d in self.service.diagnostics(uri, text)]})

        if method == "textDocument/completion":
            uri, text = self._document(params)
            position = self._position(params)
            return self._response(request_id, {"isIncomplete": False, "items": [self._completion(i) for i in self.service.completions(text, position)]})

        if method == "textDocument/hover":
            uri, text = self._document(params)
            hover = self.service.hover(uri, text, self._position(params))
            return self._response(request_id, None if hover is None else {"contents": {"kind": "plaintext", "value": hover.contents}})

        if method == "textDocument/definition":
            uri, text = self._document(params)
            location = self.service.definition(uri, text, self._position(params))
            return self._response(request_id, None if location is None else self._location(location))

        if method == "textDocument/documentSymbol":
            uri, text = self._document(params)
            return self._response(request_id, [self._symbol(s) for s in self.service.document_symbols(uri, text)])

        if method == "textDocument/formatting":
            uri, text = self._document(params)
            return self._response(request_id, [self._edit(e) for e in self.service.format(uri, text)])

        if request_id is not None:
            return self._error(request_id, -32601, f"Method not supported: {method}")
        return None

    def run_stdio(self) -> None:
        while True:
            message = self._read_message()
            if message is None:
                return
            response = self.handle(message)
            if response is not None:
                self._write_message(response)
            if message.get("method") == "exit":
                return

    def _document(self, params: dict[str, Any]) -> tuple[str, str]:
        uri = params["textDocument"]["uri"]
        return uri, self.documents.get(uri, "")

    @staticmethod
    def _position(params: dict[str, Any]) -> Position:
        position = params["position"]
        return Position(position["line"], position["character"])

    @staticmethod
    def _response(request_id: Any, result: Any) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}

    @staticmethod
    def _diagnostic(d: Any) -> dict[str, Any]:
        return {
            "range": LSPServer._range(d.range),
            "severity": 1,
            "source": d.source,
            "message": d.message,
        }

    @staticmethod
    def _completion(item: Any) -> dict[str, Any]:
        return {"label": item.label, "detail": item.detail}

    @staticmethod
    def _location(location: Any) -> dict[str, Any]:
        return {"uri": location.uri, "range": LSPServer._range(location.range)}

    @staticmethod
    def _symbol(symbol: Any) -> dict[str, Any]:
        return {
            "name": symbol.name,
            "kind": 13 if symbol.kind == "application" else 12,
            "range": LSPServer._range(symbol.range),
            "selectionRange": LSPServer._range(symbol.selection_range),
            "children": [LSPServer._symbol(child) for child in symbol.children],
        }

    @staticmethod
    def _edit(edit: Any) -> dict[str, Any]:
        return {"range": LSPServer._range(edit.range), "newText": edit.new_text}

    @staticmethod
    def _range(value: Any) -> dict[str, Any]:
        return {
            "start": {"line": value.start.line, "character": value.start.character},
            "end": {"line": value.end.line, "character": value.end.character},
        }

    @staticmethod
    def _read_message() -> dict[str, Any] | None:
        headers: dict[str, str] = {}
        while True:
            line = sys.stdin.buffer.readline()
            if not line:
                return None
            decoded = line.decode("ascii").strip()
            if not decoded:
                break
            key, _, value = decoded.partition(":")
            headers[key.lower()] = value.strip()

        length = int(headers.get("content-length", "0"))
        if length <= 0:
            return None
        body = sys.stdin.buffer.read(length)
        return json.loads(body.decode("utf-8"))

    @staticmethod
    def _write_message(message: dict[str, Any]) -> None:
        body = json.dumps(message, separators=(",", ":")).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
        sys.stdout.buffer.write(header + body)
        sys.stdout.buffer.flush()


def main() -> int:
    LSPServer().run_stdio()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
