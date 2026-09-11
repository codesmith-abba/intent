import tempfile
from pathlib import Path

from itl.build.models import BuildItem, BuildPlan
from itl.build.results import BuildResult, BuildResults, BuildResultStatus
from itl.cache.decision import CacheStatus
from itl.emit import EmitStatus, Emitter, UnsafeOutputPathError


def _plan(source="pages/home.itl", removed=None):
    return BuildPlan(
        items=[BuildItem(source=source, status=CacheStatus.MISS)],
        removed=list(removed or []),
    )


def _results(source="pages/home.itl", output="hello"):
    results = BuildResults()
    results.add(BuildResult(source=source, status=BuildResultStatus.SUCCESS, output=output))
    return results


def test_new_output_is_created():
    with tempfile.TemporaryDirectory() as directory:
        emitter = Emitter(directory)
        result = emitter.emit(_plan(), _results())
        path = Path(directory) / "pages/home.generated"
        assert result.created[0].path == path
        assert path.read_text() == "hello"


def test_modified_output_is_replaced_atomically():
    with tempfile.TemporaryDirectory() as directory:
        emitter = Emitter(directory)
        emitter.emit(_plan(), _results("pages/home.itl", "old"))
        result = emitter.emit(_plan(), _results("pages/home.itl", "new"))
        assert result.modified
        assert (Path(directory) / "pages/home.generated").read_text() == "new"


def test_unchanged_output_is_not_rewritten():
    with tempfile.TemporaryDirectory() as directory:
        emitter = Emitter(directory)
        emitter.emit(_plan(), _results())
        result = emitter.emit(_plan(), _results())
        assert result.unchanged


def test_removed_output_is_deleted_from_manifest():
    with tempfile.TemporaryDirectory() as directory:
        emitter = Emitter(directory)
        emitter.emit(_plan(), _results())
        removal_plan = BuildPlan(removed=["pages/home.itl"])
        result = emitter.emit(removal_plan, BuildResults())
        assert result.removed
        assert not (Path(directory) / "pages/home.generated").exists()


def test_failed_generation_is_never_emitted():
    with tempfile.TemporaryDirectory() as directory:
        results = BuildResults()
        results.add(BuildResult(source="pages/home.itl", status=BuildResultStatus.FAILED, output="bad"))
        emitter = Emitter(directory)
        result = emitter.emit(_plan(), results)
        assert not result.results
        assert not (Path(directory) / "pages/home.generated").exists()


def test_failed_validation_result_is_never_emitted():
    with tempfile.TemporaryDirectory() as directory:
        results = BuildResults()
        results.add(BuildResult(source="pages/home.itl", status=BuildResultStatus.FAILED, output="invalid"))
        emitter = Emitter(directory)
        result = emitter.emit(_plan(), results)
        assert not result.results
        assert not (Path(directory) / "pages/home.generated").exists()


def test_atomic_write_failure_is_reported_and_original_is_preserved():
    with tempfile.TemporaryDirectory() as directory:
        emitter = Emitter(directory)
        emitter.emit(_plan(), _results("pages/home.itl", "original"))

        original = Emitter._atomic_write

        def fail(path, content):
            raise OSError("disk failure")

        Emitter._atomic_write = staticmethod(fail)
        try:
            result = emitter.emit(_plan(), _results("pages/home.itl", "replacement"))
        finally:
            Emitter._atomic_write = original

        assert result.failed
        assert (Path(directory) / "pages/home.generated").read_text() == "original"


def test_dry_run_reports_without_modifying_files():
    with tempfile.TemporaryDirectory() as directory:
        emitter = Emitter(directory)
        result = emitter.emit(_plan(), _results(), dry_run=True)
        assert result.created
        assert not (Path(directory) / "pages/home.generated").exists()
        assert not (Path(directory) / ".project/emit/manifest.json").exists()


def test_stale_output_is_removed_when_current_sources_are_supplied():
    with tempfile.TemporaryDirectory() as directory:
        emitter = Emitter(directory)
        emitter.emit(_plan(), _results())
        result = emitter.emit(BuildPlan(), BuildResults(), current_sources=set())
        assert result.removed
        assert not (Path(directory) / "pages/home.generated").exists()


def test_output_cannot_escape_target_root():
    with tempfile.TemporaryDirectory() as directory:
        emitter = Emitter(directory, mapper=lambda source: Path("../outside.txt"))
        result = emitter.emit(_plan(), _results())
        assert result.failed
        assert isinstance(result.failed[0].error, UnsafeOutputPathError)


def test_reserved_project_state_cannot_be_emitted():
    with tempfile.TemporaryDirectory() as directory:
        emitter = Emitter(directory, mapper=lambda source: Path(".project/output.txt"))
        result = emitter.emit(_plan(), _results())
        assert result.failed
        assert isinstance(result.failed[0].error, UnsafeOutputPathError)
