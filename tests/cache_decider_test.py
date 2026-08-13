from pathlib import Path
from tempfile import TemporaryDirectory

from itl.cache.cache import Cache
from itl.cache.decider import CacheDecider
from itl.cache.decision import CacheStatus


def test_cache_miss():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        source = root / "home.itl"

        source.write_text(
            "page $home {}",
            encoding="utf-8",
        )

        cache = Cache(root)

        decider = CacheDecider(cache)

        decision = decider.decide(source)

        assert decision.status == CacheStatus.MISS


def test_cache_hit():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        source = root / "home.itl"

        source.write_text(
            "page $home {}",
            encoding="utf-8",
        )

        cache = Cache(root)

        cache.put(
            source,
            output="home",
        )

        cache.save()

        decider = CacheDecider(cache)

        decision = decider.decide(source)

        assert decision.status == CacheStatus.HIT


def test_cache_invalidated():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        source = root / "home.itl"

        source.write_text(
            "page $home {}",
            encoding="utf-8",
        )

        cache = Cache(root)

        cache.put(
            source,
            output="home",
        )

        cache.save()

        source.write_text(
            "page $home { intent $(Updated) }",
            encoding="utf-8",
        )

        decider = CacheDecider(cache)

        decision = decider.decide(source)

        assert (
            decision.status
            == CacheStatus.INVALIDATED
        )


if __name__ == "__main__":

    test_cache_miss()
    test_cache_hit()
    test_cache_invalidated()

    print(
        "All cache decider tests passed."
    )