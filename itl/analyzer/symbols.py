from dataclasses import dataclass

from itl.parser.ast import Node


@dataclass(slots=True)
class Symbol:

    name: str

    node: Node