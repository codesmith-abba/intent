import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path

from itl.runtime.manifest import BrowserManifestBuilder


class IRWriter:

    def __init__(self, root: str | Path = ".project"):
        self.root = Path(root)

    def write(self, project):
        root = self.root

        root.mkdir(parents=True, exist_ok=True)

        (root / "assets").mkdir(exist_ok=True)
        (root / "cache").mkdir(exist_ok=True)
        (root / "logs").mkdir(exist_ok=True)

        self._write_json(root / "app.json", asdict(project))

        framework = None
        if project.system is not None:
            framework = project.system.frontend

        metadata = {
            "version": "0.1.0",
            "framework": framework,
            "target": project.target,
        }
        self._write_json(root / "metadata.json", metadata)

        graph = {
            "pages": [
                page.name
                for page in project.pages
            ]
        }
        self._write_json(root / "graph.json", graph)

        BrowserManifestBuilder().write([project], root / "runtime.json")

    @staticmethod
    def _write_json(path: Path, value: object) -> None:
        """Persist one generated artifact atomically and durably."""
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(value, indent=4, ensure_ascii=False) + "\n"
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as temporary:
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        try:
            os.replace(temporary_path, path)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise
