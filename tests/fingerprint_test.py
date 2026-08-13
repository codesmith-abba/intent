from pathlib import Path

from itl.cache.fingerprint import SourceFingerprint


TEST_FILE = Path("tests/fingerprint_source.itl")


def test_fingerprint_is_stable():

    TEST_FILE.write_text(
        "section $home {}",
        encoding="utf-8",
    )

    first = SourceFingerprint.calculate(
        TEST_FILE
    )

    second = SourceFingerprint.calculate(
        TEST_FILE
    )

    assert first == second


def test_fingerprint_changes_when_source_changes():

    TEST_FILE.write_text(
        "section $home {}",
        encoding="utf-8",
    )

    first = SourceFingerprint.calculate(
        TEST_FILE
    )

    TEST_FILE.write_text(
        "section $home { intent $(Updated) }",
        encoding="utf-8",
    )

    second = SourceFingerprint.calculate(
        TEST_FILE
    )

    assert first != second


def test_fingerprint_is_sha256():

    TEST_FILE.write_text(
        "section $home {}",
        encoding="utf-8",
    )

    fingerprint = SourceFingerprint.calculate(
        TEST_FILE
    )

    assert len(fingerprint) == 64


if __name__ == "__main__":

    test_fingerprint_is_stable()
    test_fingerprint_changes_when_source_changes()
    test_fingerprint_is_sha256()

    print(
        "All fingerprint tests passed."
    )