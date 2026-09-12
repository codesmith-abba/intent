from pathlib import Path
from tempfile import TemporaryDirectory

from itl.build.models import BuildItem, BuildPlan
from itl.build.scheduler import BuildScheduler
from itl.cache.cache import Cache
from itl.cache.decision import CacheStatus


def test_scheduler_handles_large_dependency_graph_deterministically():
    count = 5000
    items = [
        BuildItem(source=f"page-{index:05d}.itl", status=CacheStatus.MISS)
        for index in range(count)
    ]
    for index in range(1, count):
        items[index].dependencies.add(items[index - 1].source)

    schedule = BuildScheduler().schedule(BuildPlan(items=items))

    assert len(schedule.batches) == count
    assert list(schedule.sources) == [item.source for item in items]


def test_cache_recovers_from_corrupt_state():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        cache_file = root / ".project" / "cache" / "entries.json"
        cache_file.parent.mkdir(parents=True)
        cache_file.write_text("{not valid json", encoding="utf-8")

        cache = Cache(root)
        assert cache.store.entries == {}
        assert not cache_file.exists()
        assert (root / ".project" / "cache" / "entries.corrupt").exists()


def test_cache_state_is_recoverable_after_quarantine():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        cache_file = root / ".project" / "cache" / "entries.json"
        cache_file.parent.mkdir(parents=True)
        cache_file.write_text("{not valid json", encoding="utf-8")

        cache = Cache(root)
        source = root / "app.itl"
        source.write_text("app", encoding="utf-8")
        cache.put(source)
        cache.save()

        reloaded = Cache(root)
        assert reloaded.get(source) is not None


if __name__ == "__main__":
    test_scheduler_handles_large_dependency_graph_deterministically()
    test_cache_recovers_from_corrupt_state()
    test_cache_state_is_recoverable_after_quarantine()
    print("All production stress tests passed.")
