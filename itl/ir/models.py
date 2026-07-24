from dataclasses import dataclass, field


@dataclass(slots=True)
class IRHero:
    image: str | None = None
    headline: str | None = None
    subtitle: str | None = None
    action: str | None = None


@dataclass(slots=True)
class IRSection:
    name: str


@dataclass(slots=True)
class IRPage:
    name: str
    theme: str

    hero: IRHero | None = None

    sections: list[IRSection] = field(default_factory=list)


@dataclass(slots=True)
class IRApplication:
    name: str

    target: str

    framework: str

    pages: list[IRPage] = field(default_factory=list)