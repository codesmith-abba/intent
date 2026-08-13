from pathlib import Path

from .models import CacheEntry
from .persistence import CachePersistence


class CacheStore:

    def __init__(
        self,
        root: str | Path | None = None,
    ):

        self.entries: dict[str, CacheEntry] = {}

        self.persistence = None

        if root is not None:

            self.persistence = (
                CachePersistence(root)
            )

            self.entries = (
                self.persistence.load()
            )

    def get(
        self,
        source: str,
    ) -> CacheEntry | None:

        return self.entries.get(source)

    def set(
        self,
        entry: CacheEntry,
    ):

        self.entries[entry.source] = entry

    def remove(
        self,
        source: str,
    ):

        self.entries.pop(
            source,
            None,
        )

    def clear(self):

        self.entries.clear()

    def has(
        self,
        source: str,
    ) -> bool:

        return source in self.entries

    def save(self):

        if self.persistence is None:
            return

        self.persistence.save(
            self.entries
        )