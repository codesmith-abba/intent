from pathlib import Path

from .fingerprint import SourceFingerprint
from .models import CacheEntry
from .store import CacheStore
from .validator import CacheValidator


class Cache:

    def __init__(
        self,
        root: str | Path,
    ):

        self.store = CacheStore(root)

    def get(
        self,
        source: str | Path,
    ) -> CacheEntry | None:

        source = str(source)

        entry = self.store.get(source)

        if not CacheValidator.is_valid(
            entry,
            source,
        ):
            return None

        return entry

    def put(
        self,
        source: str | Path,
        output: str | None = None,
        metadata: dict | None = None,
    ):

        source = str(source)

        fingerprint = (
            SourceFingerprint.calculate(source)
        )

        entry = CacheEntry(
            source=source,
            fingerprint=fingerprint,
            output=output,
            metadata=metadata or {},
        )

        self.store.set(entry)

    def save(self):

        self.store.save()

    def clear(self):

        self.store.clear()

        self.save()
    
    def remove_missing_sources(
        self,
        sources: set[str],
    ):

        stale = set(self.store.entries) - sources

        for source in stale:

            self.store.remove(source)
    
    def remove(
        self,
        source: str | Path,
    ):

        source = str(source)

        self.store.remove(source)