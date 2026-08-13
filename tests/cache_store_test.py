from itl.cache.models import CacheEntry
from itl.cache.store import CacheStore


store = CacheStore()

entry = CacheEntry(
    source="home.itl",
    fingerprint="abc123",
)

store.set(entry)

assert store.has("home.itl")
assert store.get("home.itl").fingerprint == "abc123" # type: ignore

store.remove("home.itl")

assert not store.has("home.itl")

print("Cache store works.")