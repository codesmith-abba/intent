import json
import os
import tempfile
from pathlib import Path

from .models import CacheEntry


class CachePersistence:

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.cache_dir = self.root / ".project" / "cache"
        self.cache_file = self.cache_dir / "entries.json"

    def load(self) -> dict[str, CacheEntry]:
        if not self.cache_file.exists():
            return {}
        try:
            data = json.loads(self.cache_file.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Cache state must be an object.")
            entries: dict[str, CacheEntry] = {}
            for source, entry in data.items():
                if not isinstance(source, str) or not isinstance(entry, dict):
                    raise ValueError("Invalid cache entry.")
                entries[source] = CacheEntry(
                    source=entry["source"],
                    fingerprint=entry["fingerprint"],
                    output=entry.get("output"),
                    metadata=entry.get("metadata", {}),
                )
            return entries
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            self._quarantine_corrupt_state()
            return {}

    def save(self, entries: dict[str, CacheEntry]):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        data = {
            source: {
                "source": entry.source,
                "fingerprint": entry.fingerprint,
                "output": entry.output,
                "metadata": entry.metadata,
            }
            for source, entry in entries.items()
        }
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=self.cache_dir, suffix=".tmp", delete=False
        ) as temp:
            json.dump(data, temp, indent=2)
            temp.write("\n")
            temp.flush()
            os.fsync(temp.fileno())
            temp_path = Path(temp.name)
        try:
            os.replace(temp_path, self.cache_file)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def _quarantine_corrupt_state(self) -> None:
        """Move unreadable state aside so the next build can recover cleanly."""
        if not self.cache_file.exists():
            return
        backup = self.cache_file.with_suffix(".corrupt")
        try:
            if backup.exists():
                backup.unlink()
            os.replace(self.cache_file, backup)
        except OSError:
            # A cache is disposable state; inability to quarantine must not
            # prevent a clean rebuild from proceeding.
            pass
