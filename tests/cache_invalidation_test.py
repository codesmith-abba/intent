from pathlib import Path

from itl.cache.fingerprint import SourceFingerprint
from itl.cache.invalidation import CacheInvalidator
from itl.cache.models import CacheEntry


TEST_FILE = Path(
    "tests/cache_invalidation_source.itl"
)


def test_changed_source_is_invalid():

    TEST_FILE.write_text(
        "section $home {}",
        encoding="utf-8",
    )

    fingerprint = (
        SourceFingerprint.calculate(TEST_FILE)
    )

    entry = CacheEntry(
        source=str(TEST_FILE),
        fingerprint=fingerprint,
    )

    TEST_FILE.write_text(
        "section $home { intent $(Updated) }",
        encoding="utf-8",
    )

    assert CacheInvalidator.is_invalid(
        entry,
        TEST_FILE,
    )


def test_unchanged_source_is_not_invalid():

    TEST_FILE.write_text(
        "section $home {}",
        encoding="utf-8",
    )

    fingerprint = (
        SourceFingerprint.calculate(TEST_FILE)
    )

    entry = CacheEntry(
        source=str(TEST_FILE),
        fingerprint=fingerprint,
    )

    assert not CacheInvalidator.is_invalid(
        entry,
        TEST_FILE,
    )


def test_missing_entry_is_invalid():

    TEST_FILE.write_text(
        "section $home {}",
        encoding="utf-8",
    )

    assert CacheInvalidator.is_invalid(
        None,
        TEST_FILE,
    )


if __name__ == "__main__":

    test_changed_source_is_invalid()
    test_unchanged_source_is_not_invalid()
    test_missing_entry_is_invalid()

    print(
        "All cache invalidation tests passed."
    )