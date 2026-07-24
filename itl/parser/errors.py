class ITLError(Exception):
    """Base class for all ITL errors."""
    pass


class LexerError(ITLError):
    """Raised when scanning source code fails."""
    pass


class ParseError(ITLError):
    """Raised when parsing tokens fails."""
    pass