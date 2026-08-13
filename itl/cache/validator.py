from .fingerprint import SourceFingerprint
from .models import CacheEntry


class CacheValidator:

    @staticmethod
    def is_valid(
        entry: CacheEntry | None,
        source: str,
    ) -> bool:

        if entry is None:
            return False

        current_fingerprint = (
            SourceFingerprint.calculate(source)
        )

        return (
            entry.fingerprint
            == current_fingerprint
        )