from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class ProjectState:

    name: str

    version: str = "1"

    entrypoint: Optional[str] = None

    generator_version: Optional[str] = None

    schema_version: int = 1