from pathlib import Path
from tempfile import TemporaryDirectory

from itl.cache.cache import Cache


def test_cache_hit():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        source = root / "home.itl"

        source.write_text(
            "section $home {}",
            encoding="utf-8",
        )

        cache = Cache(root)

        cache.put(
            source,
            output="home",
        )

        cache.save()

        new_cache = Cache(root)

        entry = new_cache.get(source)

        assert entry is not None
        assert entry.output == "home"


def test_cache_miss_after_source_change():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        source = root / "home.itl"

        source.write_text(
            "section $home {}",
            encoding="utf-8",
        )

        cache = Cache(root)

        cache.put(
            source,
            output="home",
        )

        cache.save()

        source.write_text(
            "section $home { intent $(Updated) }",
            encoding="utf-8",
        )

        new_cache = Cache(root)

        assert new_cache.get(source) is None


def test_cache_miss_without_entry():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        source = root / "home.itl"

        source.write_text(
            "section $home {}",
            encoding="utf-8",
        )

        cache = Cache(root)

        assert cache.get(source) is None

def test_remove_missing_sources():

    with TemporaryDirectory() as directory:

        root = Path(directory)

        home = root / "home.itl"
        navigation = root / "navigation.itl"

        home.write_text(
            "page $home {}",
            encoding="utf-8",
        )

        navigation.write_text(
            "section $navigation {}",
            encoding="utf-8",
        )

        cache = Cache(root)

        cache.put(home)
        cache.put(navigation)

        cache.save()

        cache.remove_missing_sources(
            {str(home)}
        )

        cache.save()

        new_cache = Cache(root)

        assert new_cache.get(home) is not None

        assert new_cache.get(
            navigation
        ) is None


if __name__ == "__main__":

    test_cache_hit()
    test_cache_miss_after_source_change()
    test_cache_miss_without_entry()
    test_remove_missing_sources()

    print(
        "All cache tests passed."
    )