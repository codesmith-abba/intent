from dataclasses import dataclass, field
from typing import Optional, Literal, List

# Base Node class
@dataclass(slots=True)
class Node:
    pass

# Base Intent node
@dataclass(slots=True)
class IntentNode(Node):

    intent: Optional[str]

# Base Import node
@dataclass(slots=True)
class ImportNode(IntentNode):

    imports: Optional[list[str]]

# Framework node
@dataclass(slots=True)
class Framework(Node):
    value: Literal["react", "vue", "angular", "svelte", 'django'] | str = "react"

# Engine node
@dataclass(slots=True)
class Engine(Node):
    value: str

# Provider node
@dataclass(slots=True)
class Provider(Node):
    value: str

# API node
@dataclass(slots=True)
class API(Node):
    value: str

# Block nodes
@dataclass(slots=True)
class Frontend(IntentNode):
    framework: Framework | None = None

# Backend
@dataclass(slots=True)
class Backend(IntentNode):
    framework: Framework | None = None
    api: API | None = None

# Database
@dataclass(slots=True)
class Database(IntentNode):
    engine: Engine | None = None

# Cache
@dataclass(slots=True)
class Cache(IntentNode):
    engine: Engine | None = None

# Storage
@dataclass(slots=True)
class Storage(IntentNode):
    provider: Provider | None = None

# System node
@dataclass(slots=True)
class System(IntentNode):

    frontend: Frontend | None = None

    backend: Backend | None = None

    database: Database | None = None

    cache: Cache | None = None

    storage: Storage | None = None

# App node
@dataclass(slots=True)
class App(ImportNode):
    name: str

    pages: List["Page"] | None = field(default_factory=list)

    system: System | None = None

    target: Literal['web', 'mobile'] | str = "web"

# Page node
@dataclass(slots=True)
class Page(ImportNode):
    name: str

    theme: Optional[str] = None

    hero: Optional["Hero"] = None

    sections: List["Section"] = field(default_factory=list)

# Hero node
@dataclass(slots=True)
class Hero(IntentNode):
    name: str

    image: Optional[str] = None
    headline: Optional[str] = None
    subtitle: Optional[str] = None
    action: Optional[str] = None

# Section node
@dataclass(slots=True)
class Section(ImportNode):
    name: str

# Model node
@dataclass(slots=True)
class Model(ImportNode):
    pass