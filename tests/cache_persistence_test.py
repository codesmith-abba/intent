from pathlib import Path
from tempfile import TemporaryDirectory

from itl.cache.models import CacheEntry
from itl.cache.persistence import CachePersistence


def test_save_and_load():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        persistence = CachePersistence(
            root
        )

        entries = {
            "home.itl": CacheEntry(
                source="home.itl",
                fingerprint="abc123",
                output="home",
                metadata={
                    "type": "page",
                },
            )
        }

        persistence.save(entries)

        loaded = persistence.load()

        assert "home.itl" in loaded

        entry = loaded["home.itl"]

        assert entry.source == "home.itl"
        assert entry.fingerprint == "abc123"
        assert entry.output == "home"

        assert entry.metadata == {
            "type": "page",
        }


def test_missing_cache_returns_empty():

    with TemporaryDirectory() as directory:

        persistence = CachePersistence(
            directory
        )

        assert persistence.load() == {}


def test_cache_directory_is_created():

    with TemporaryDirectory() as directory:

        persistence = CachePersistence(
            directory
        )

        persistence.save({})

        assert persistence.cache_file.exists()


if __name__ == "__main__":

    test_save_and_load()
    test_missing_cache_returns_empty()
    test_cache_directory_is_created()

    print(
        "All cache persistence tests passed."
    )