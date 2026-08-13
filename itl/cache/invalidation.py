from .fingerprint import SourceFingerprint
from .models import CacheEntry


class CacheInvalidator:

    @staticmethod
    def is_invalid(
        entry: CacheEntry | None,
        source: str,
    ) -> bool:

        if entry is None:
            return True

        current_fingerprint = (
            SourceFingerprint.calculate(source)
        )

        return (
            entry.fingerprint
            != current_fingerprint
        )