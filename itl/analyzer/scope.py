from .errors import SemanticError
from .symbols import Symbol


class Scope:

    def __init__(self, parent=None):

        self.parent = parent

        self.symbols = {}

    def define(self, symbol: Symbol):

        if symbol.name in self.symbols:

            raise SemanticError(
                f"'{symbol.name}' is already defined."
            )

        self.symbols[symbol.name] = symbol

    def resolve(self, name: str):

        scope = self

        while scope:

            symbol = scope.symbols.get(name)

            if symbol:

                return symbol

            scope = scope.parent

        return None