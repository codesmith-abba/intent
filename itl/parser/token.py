from dataclasses import dataclass

from .token_type import TokenType


@dataclass(slots=True)
class Token:
    type: TokenType
    lexeme: str
    line: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.lexeme!r}, line={self.line})"