from dataclasses import dataclass, field
from typing import Optional


# ==========================================================
# Base
# ==========================================================

@dataclass(slots=True)
class GIRNode:
    intent: str | None


# ==========================================================
# Application
# ==========================================================

@dataclass(slots=True)
class GIRApplication(GIRNode):

    name: str

    target: str

    system: Optional["GIRSystem"] = None

    pages: list["GIRPage"] = field(default_factory=list)


# ==========================================================
# Page
# ==========================================================

@dataclass(slots=True)
class GIRPage(GIRNode):

    name: str

    theme: Optional[str] = None

    components: list["GIRNode"] = field(default_factory=list)


# ==========================================================
# Components
# ==========================================================

@dataclass(slots=True)
class GIRHero(GIRNode):

    name: str

    image: Optional[str] = None

    headline: Optional[str] = None

    subtitle: Optional[str] = None

    action: Optional[str] = None


@dataclass(slots=True)
class GIRSection(GIRNode):

    name: str

    children: list["GIRSection"] = field(default_factory=list)


# ==========================================================
# System
# ==========================================================

@dataclass(slots=True)
class GIRSystem(GIRNode):

    frontend: Optional[str] = None

    backend: Optional[str] = None

    api: Optional[str] = None

    database: Optional[str] = None

    cache: Optional[str] = None

    storage: Optional[str] = None