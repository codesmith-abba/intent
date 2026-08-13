from pathlib import Path

from .cache import Cache
from .decision import CacheDecision, CacheStatus


class CacheDecider:

    def __init__(
        self,
        cache: Cache,
    ):

        self.cache = cache

    def decide(
        self,
        source: str | Path,
    ) -> CacheDecision:

        source = str(source)

        entry = self.cache.store.get(source)

        if entry is None:

            return CacheDecision(
                status=CacheStatus.MISS,
                source=source,
                reason="No cached entry exists.",
            )

        if self.cache.get(source) is not None:

            return CacheDecision(
                status=CacheStatus.HIT,
                source=source,
                reason=(
                    "Source fingerprint matches "
                    "cached entry."
                ),
            )

        return CacheDecision(
            status=CacheStatus.INVALIDATED,
            source=source,
            reason=(
                "Source fingerprint changed."
            ),
        )