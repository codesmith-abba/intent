import json
from pathlib import Path

from .models import CacheEntry


class CachePersistence:

    def __init__(
        self,
        root: str | Path,
    ):

        self.root = Path(root)

        self.cache_dir = (
            self.root
            / ".project"
            / "cache"
        )

        self.cache_file = (
            self.cache_dir
            / "entries.json"
        )

    def load(self) -> dict[str, CacheEntry]:

        if not self.cache_file.exists():
            return {}

        data = json.loads(
            self.cache_file.read_text(
                encoding="utf-8"
            )
        )

        return {
            source: CacheEntry(
                source=entry["source"],
                fingerprint=entry["fingerprint"],
                output=entry.get("output"),
                metadata=entry.get(
                    "metadata",
                    {},
                ),
            )
            for source, entry in data.items()
        }

    def save(
        self,
        entries: dict[str, CacheEntry],
    ):

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = {
            source: {
                "source": entry.source,
                "fingerprint": entry.fingerprint,
                "output": entry.output,
                "metadata": entry.metadata,
            }
            for source, entry in entries.items()
        }

        self.cache_file.write_text(
            json.dumps(
                data,
                indent=2,
            ),
            encoding="utf-8",
        )