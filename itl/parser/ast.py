from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True)
class Node:
    pass
    # intent: str | None = None


@dataclass(slots=True)
class App(Node):
    name: str
    pages: list["Page"] = field(default_factory=list)

    target: Optional[str] = None
    framework: Optional[str] = None


@dataclass(slots=True)
class Page(Node):
    name: str

    theme: Optional[str] = None

    hero: Optional["Hero"] = None

    sections: list["Section"] = field(default_factory=list)


@dataclass(slots=True)
class Hero(Node):
    name: str

    image: Optional[str] = None
    headline: Optional[str] = None
    subtitle: Optional[str] = None
    action: Optional[str] = None


@dataclass(slots=True)
class Section(Node):
    name: str