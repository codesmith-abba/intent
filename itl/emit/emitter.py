import json
import os
import tempfile
from pathlib import Path
from typing import Callable, Mapping

from itl.build.models import BuildPlan
from itl.build.results import BuildResults, BuildResultStatus
from itl.emit.mapper import OutputMapper, RelativeOutputMapper
from itl.emit.models import EmitResult, EmitResults, EmitStatus


class EmitError(Exception):
    pass


class UnsafeOutputPathError(EmitError):
    pass


class Emitter:
    """Write only validated build results into a target project."""

    _RESERVED = {".git", ".project", ".gitignore"}
    _MANIFEST = ".project/emit/manifest.json"

    def __init__(
        self,
        target_root: str | Path,
        mapper: OutputMapper | Callable[[str], Path] | None = None,
        manifest_path: str | Path | None = None,
    ):
        self.target_root = Path(target_root).resolve()
        self.mapper = mapper or RelativeOutputMapper()
        self.manifest_path = (
            Path(manifest_path).resolve()
            if manifest_path is not None
            else self.target_root / self._MANIFEST
        )

    def emit(
        self,
        plan: BuildPlan,
        results: BuildResults,
        *,
        dry_run: bool = False,
        current_sources: set[str] | None = None,
    ) -> EmitResults:
        by_source = {result.source: result for result in results.results}
        emitted = EmitResults()
        manifest = self._load_manifest()

        for item in plan.items:
            result = by_source.get(item.source)
            if (
                result is None
                or result.status != BuildResultStatus.SUCCESS
                or result.validation_report is None
                or not result.validation_report.passed
            ):
                continue
            if not isinstance(result.output, str):
                emitted.add(EmitResult(item.source, EmitStatus.FAILED, error=EmitError("Emitter requires text output.")))
                continue

            try:
                path = self._safe_path(self._mapped_path(item.source))
                status = self._write(path, result.output, dry_run=dry_run)
                emitted.add(EmitResult(item.source, status, path=path))
                if not dry_run:
                    manifest[item.source] = path.relative_to(self.target_root).as_posix()
            except Exception as error:
                emitted.add(EmitResult(item.source, EmitStatus.FAILED, error=error))

        for source in sorted(plan.removed):
            relative = manifest.get(source)
            if relative is None:
                continue
            try:
                path = self._safe_path(Path(relative))
                if path.exists():
                    if not dry_run:
                        path.unlink()
                    emitted.add(EmitResult(source, EmitStatus.REMOVED, path=path))
                else:
                    emitted.add(EmitResult(source, EmitStatus.UNCHANGED, path=path))
                if not dry_run:
                    manifest.pop(source, None)
            except Exception as error:
                emitted.add(EmitResult(source, EmitStatus.FAILED, error=error))

        if current_sources is not None:
            stale = sorted(set(manifest) - set(current_sources) - set(plan.removed))
            for source in stale:
                try:
                    path = self._safe_path(Path(manifest[source]))
                    if path.exists():
                        if not dry_run:
                            path.unlink()
                        emitted.add(EmitResult(source, EmitStatus.REMOVED, path=path))
                    if not dry_run:
                        manifest.pop(source, None)
                except Exception as error:
                    emitted.add(EmitResult(source, EmitStatus.FAILED, error=error))

        if not dry_run and not emitted.failed:
            self._save_manifest(manifest)
        return emitted

    def _mapped_path(self, source: str) -> Path:
        mapped = self.mapper.map(source) if hasattr(self.mapper, "map") else self.mapper(source)
        return Path(mapped)

    def _safe_path(self, relative: Path) -> Path:
        if relative.is_absolute():
            raise UnsafeOutputPathError(f"Output mapper must return a relative path: {relative}")
        candidate = (self.target_root / relative).resolve()
        try:
            candidate.relative_to(self.target_root)
        except ValueError as error:
            raise UnsafeOutputPathError(f"Output path escapes target root: {relative}") from error
        if any(part in self._RESERVED for part in candidate.relative_to(self.target_root).parts):
            raise UnsafeOutputPathError(f"Output path targets reserved compiler/project state: {relative}")
        return candidate

    def _write(self, path: Path, content: str, *, dry_run: bool) -> EmitStatus:
        if path.exists() and path.read_text(encoding="utf-8") == content:
            return EmitStatus.UNCHANGED
        status = EmitStatus.MODIFIED if path.exists() else EmitStatus.CREATED
        if dry_run:
            return status
        path.parent.mkdir(parents=True, exist_ok=True)
        self._atomic_write(path, content)
        return status

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        except Exception:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            raise

    def _load_manifest(self) -> dict[str, str]:
        try:
            data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            return dict(data) if isinstance(data, dict) else {}
        except FileNotFoundError:
            return {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_manifest(self, manifest: Mapping[str, str]) -> None:
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._atomic_write(
            self.manifest_path,
            json.dumps(dict(sorted(manifest.items())), indent=2) + "\n",
        )
