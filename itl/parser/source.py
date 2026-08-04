from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SourceFile:

    path: Path

    text: str