from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


@dataclass(frozen=True, slots=True)
class Position:
    line: int
    character: int


@dataclass(frozen=True, slots=True)
class Range:
    start: Position
    end: Position


class DiagnosticSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFORMATION = "information"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    message: str
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR
    range: Range = field(
        default_factory=lambda: Range(Position(0, 0), Position(0, 0))
    )
    source: str = "itl"


@dataclass(frozen=True, slots=True)
class CompletionItem:
    label: str
    kind: str = "keyword"
    detail: str = "ITL"


@dataclass(frozen=True, slots=True)
class Hover:
    contents: str
    range: Range | None = None


@dataclass(frozen=True, slots=True)
class Location:
    uri: str
    range: Range


@dataclass(frozen=True, slots=True)
class DocumentSymbol:
    name: str
    kind: str
    range: Range
    selection_range: Range
    children: tuple["DocumentSymbol", ...] = ()


@dataclass(frozen=True, slots=True)
class TextEdit:
    range: Range
    new_text: str


@dataclass(slots=True)
class AnalysisResult:
    ast: Any | None = None
    diagnostics: list[Diagnostic] = field(default_factory=list)
    symbols: list[DocumentSymbol] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.diagnostics
