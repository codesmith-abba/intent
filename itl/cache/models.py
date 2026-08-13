from dataclasses import dataclass, field


@dataclass(slots=True)
class CacheEntry:

    source: str

    fingerprint: str

    output: str | None = None

    metadata: dict = field(
        default_factory=dict
    )