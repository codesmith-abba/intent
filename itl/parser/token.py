from typing import Any, Optional
from dataclasses import dataclass
from pathlib import Path

from .token_type import TokenType


@dataclass(slots=True)
class Token:
    type: TokenType

    lexeme: str

    line: int

    literal: Optional[Any] = None

    column: Optional[int] = None

    file: Optional[Path] = None

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.lexeme!r}, Literal={self.literal}, line={self.line}, column={self.column}, file={self.file})"