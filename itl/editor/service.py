from __future__ import annotations

from dataclasses import is_dataclass, fields
from pathlib import Path
from typing import Iterable

from itl.analyzer.analyzer import Analyzer
from itl.analyzer.errors import SemanticError
from itl.parser.ast import App, Page, Section
from itl.parser.errors import ParseError
from itl.parser.lexer import KEYWORDS, Lexer
from itl.parser.parser import Parser
from itl.parser.source import SourceFile
from itl.parser.token_type import TokenType

from .models import (
    AnalysisResult,
    CompletionItem,
    Diagnostic,
    DiagnosticSeverity,
    DocumentSymbol,
    Hover,
    Location,
    Position,
    Range,
    TextEdit,
)


KEYWORD_HELP = {
    "app": "Declares the application root.",
    "page": "Declares a page inside an application.",
    "section": "Declares a section inside a page or section.",
    "hero": "Declares a page hero block.",
    "system": "Declares application system configuration.",
    "frontend": "Declares frontend configuration inside system.",
    "backend": "Declares backend configuration inside system.",
    "framework": "Sets the framework for a frontend or backend.",
    "target": "Sets the application target.",
    "theme": "Sets a page theme.",
    "intent": "Sets the natural-language intent for a node.",
    "import": "Imports a compiler module into the current app or page.",
    "image": "Sets an image path for a hero or section.",
    "headline": "Sets a hero or section headline.",
    "subtitle": "Sets a hero or section subtitle.",
    "action": "Sets a hero or section action.",
}


class EditorService:
    """Compiler-backed language tooling for ITL documents.

    This service deliberately delegates lexical, parsing, and semantic work to
    the existing compiler components. It only adapts their results to editor
    concepts such as diagnostics, symbols, completion, hover, and locations.
    """

    def analyze(self, uri: str, text: str) -> AnalysisResult:
        source = SourceFile(Path(uri), text)
        try:
            tokens = Lexer(source).scan_tokens()
            app = Parser(tokens).parse()
            Analyzer().analyze(app)
        except SyntaxError as exc:
            return AnalysisResult(diagnostics=[self._diagnostic(text, str(exc))])
        except ParseError as exc:
            return AnalysisResult(diagnostics=[self._diagnostic(text, str(exc))])
        except SemanticError as exc:
            return AnalysisResult(diagnostics=[self._diagnostic(text, str(exc))])

        symbols = self._symbols(app, text, uri)
        return AnalysisResult(ast=app, symbols=symbols)

    def diagnostics(self, uri: str, text: str) -> list[Diagnostic]:
        return self.analyze(uri, text).diagnostics

    def completions(self, text: str, position: Position) -> list[CompletionItem]:
        prefix = self._current_word(text, position)
        labels = sorted(set(KEYWORDS) | {"true", "false"})
        return [
            CompletionItem(label=label, detail="ITL keyword")
            for label in labels
            if not prefix or label.startswith(prefix)
        ]

    def hover(self, uri: str, text: str, position: Position) -> Hover | None:
        word = self._word_at(text, position)
        if not word:
            return None

        if word in KEYWORD_HELP:
            return Hover(KEYWORD_HELP[word])

        result = self.analyze(uri, text)
        for symbol in self._flatten_symbols(result.symbols):
            if symbol.name == word:
                return Hover(f"{symbol.kind}: ${symbol.name}", symbol.selection_range)
        return None

    def definition(self, uri: str, text: str, position: Position) -> Location | None:
        word = self._word_at(text, position)
        if not word:
            return None

        result = self.analyze(uri, text)
        for symbol in self._flatten_symbols(result.symbols):
            if symbol.name == word:
                return Location(uri, symbol.selection_range)
        return None

    def document_symbols(self, uri: str, text: str) -> list[DocumentSymbol]:
        return self.analyze(uri, text).symbols

    def format(self, uri: str, text: str) -> list[TextEdit]:
        """Return only conservative whitespace edits.

        Formatting is intentionally limited to trailing whitespace and a
        missing final newline. Structural indentation is left untouched so
        multiline literals and the current literal grammar cannot be changed
        accidentally.
        """
        if self.diagnostics(uri, text):
            return []

        lines = text.splitlines(keepends=True)
        edits: list[TextEdit] = []
        for index, line in enumerate(lines):
            content = line.rstrip(" \t\r\n")
            newline = "\n" if line.endswith("\n") else ""
            replacement = content + newline
            if replacement != line:
                edits.append(
                    TextEdit(
                        Range(
                            Position(index, 0),
                            Position(index, len(line.rstrip("\n"))),
                        ),
                        replacement,
                    )
                )

        if text and not text.endswith("\n"):
            last = len(lines) - 1
            edits.append(
                TextEdit(
                    Range(Position(last, len(lines[-1])), Position(last, len(lines[-1]))),
                    "\n",
                )
            )
        return edits

    def _diagnostic(self, text: str, message: str) -> Diagnostic:
        line = 0
        if "line " in message:
            try:
                line = max(int(message.rsplit("line ", 1)[1].split()[0]) - 1, 0)
            except ValueError:
                line = 0
        lines = text.splitlines() or [""]
        line = min(line, len(lines) - 1)
        return Diagnostic(
            message=message,
            severity=DiagnosticSeverity.ERROR,
            range=Range(Position(line, 0), Position(line, len(lines[line]))),
        )

    def _symbols(self, app: App, text: str, uri: str) -> list[DocumentSymbol]:
        cursor = 0

        def find_name(name: str) -> Range:
            nonlocal cursor
            needle = "$" + name
            index = text.find(needle, cursor)
            if index < 0:
                index = text.find(needle)
            if index < 0:
                return Range(Position(0, 0), Position(0, 0))
            cursor = index + len(needle)
            return self._range_for_offset(text, index + 1, len(name))

        def page_symbol(page: Page) -> DocumentSymbol:
            page_range = find_name(page.name)
            children = tuple(section_symbol(s) for s in page.sections)
            return DocumentSymbol("page:" + page.name, "page", page_range, page_range, children)

        def section_symbol(section: Section) -> DocumentSymbol:
            section_range = find_name(section.name)
            children = tuple(section_symbol(s) for s in section.sections)
            return DocumentSymbol("section:" + section.name, "section", section_range, section_range, children)

        app_range = find_name(app.name)
        return [
            DocumentSymbol(
                "app:" + app.name,
                "application",
                app_range,
                app_range,
                tuple(page_symbol(page) for page in app.pages),
            )
        ]

    def _flatten_symbols(self, symbols: Iterable[DocumentSymbol]):
        for symbol in symbols:
            yield symbol
            yield from self._flatten_symbols(symbol.children)

    @staticmethod
    def _range_for_offset(text: str, offset: int, length: int) -> Range:
        line = text.count("\n", 0, offset)
        start = text.rfind("\n", 0, offset) + 1
        character = offset - start
        return Range(Position(line, character), Position(line, character + length))

    @staticmethod
    def _current_word(text: str, position: Position) -> str:
        lines = text.splitlines()
        if position.line >= len(lines):
            return ""
        line = lines[position.line]
        left = min(position.character, len(line))
        start = left
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
            start -= 1
        return line[start:left]

    @classmethod
    def _word_at(cls, text: str, position: Position) -> str:
        lines = text.splitlines()
        if position.line >= len(lines):
            return ""
        line = lines[position.line]
        if not line:
            return ""
        index = min(position.character, len(line) - 1)
        if not (line[index].isalnum() or line[index] == "_") and index > 0:
            index -= 1
        if not (line[index].isalnum() or line[index] == "_"):
            return ""
        start = index
        end = index + 1
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
            start -= 1
        while end < len(line) and (line[end].isalnum() or line[end] == "_"):
            end += 1
        return line[start:end]
