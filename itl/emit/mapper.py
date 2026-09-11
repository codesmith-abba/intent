from pathlib import Path
from typing import Protocol


class OutputMapper(Protocol):
    def map(self, source: str) -> Path:
        """Map one build-unit identifier to a relative target path."""


class RelativeOutputMapper:
    """Deterministic default mapper for source identifiers.

    ``pages/home.itl`` becomes ``pages/home.generated``. Projects that need
    target-specific extensions should provide their own mapper.
    """

    def map(self, source: str) -> Path:
        path = Path(source)
        if path.is_absolute():
            path = Path(*path.parts[1:])
        if path.suffix in {".itl", ".intent"}:
            path = path.with_suffix(".generated")
        else:
            path = path.with_name(path.name + ".generated")
        return path
