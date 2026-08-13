from pathlib import Path

from itl.cache.fingerprint import SourceFingerprint
from itl.cache.models import CacheEntry
from itl.cache.validator import CacheValidator


TEST_FILE = Path(
    "tests/cache_validator_source.itl"
)


def test_valid_cache():

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


    assert CacheValidator.is_valid(
        entry,
        str(TEST_FILE),
    )


def test_invalid_cache_after_change():

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

    assert not CacheValidator.is_valid(
        entry,
        TEST_FILE,
    )


def test_missing_cache_is_invalid():

    TEST_FILE.write_text(
        "section $home {}",
        encoding="utf-8",
    )

    assert not CacheValidator.is_valid(
        None,
        TEST_FILE,
    )


if __name__ == "__main__":

    test_valid_cache()
    test_invalid_cache_after_change()
    test_missing_cache_is_invalid()

    print(
        "All cache validator tests passed."
    )