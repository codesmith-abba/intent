from enum import Enum, auto


class TokenType(Enum):
    # Keywords
    USE = auto()
    APP = auto()
    PAGE = auto()
    HERO = auto()
    SECTION = auto()

    TARGET = auto()
    FRAMEWORK = auto()
    THEME = auto()

    IMAGE = auto()
    HEADLINE = auto()
    SUBTITLE = auto()
    ACTION = auto()

    # Values
    STRING = auto()

    # Symbols
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()

    EOF = auto()