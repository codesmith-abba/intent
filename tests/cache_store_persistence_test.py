from pathlib import Path
from tempfile import TemporaryDirectory

from itl.cache.models import CacheEntry
from itl.cache.store import CacheStore


def test_store_persists_entries():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        store = CacheStore(root)

        store.set(
            CacheEntry(
                source="home.itl",
                fingerprint="abc123",
                output="home",
            )
        )

        store.save()

        new_store = CacheStore(root)

        entry = new_store.get(
            "home.itl"
        )

        assert entry is not None
        assert entry.fingerprint == "abc123"
        assert entry.output == "home"


def test_store_without_root_is_memory_only():

    store = CacheStore()

    store.set(
        CacheEntry(
            source="home.itl",
            fingerprint="abc123",
        )
    )

    assert store.has("home.itl")
    assert store.get(
        "home.itl"
    ).fingerprint == "abc123"


if __name__ == "__main__":

    test_store_persists_entries()
    test_store_without_root_is_memory_only()

    print(
        "All cache store persistence tests passed."
    )