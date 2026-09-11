"""Persistence for deterministic GIR fingerprints."""

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


class IncrementalStateError(RuntimeError):
    """Raised when persisted incremental-build state is invalid."""


class GIRFingerprintStore:
    """Persist GIR fingerprints as deterministic JSON."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def save(self, fingerprints: dict[str, str]) -> None:
        """Atomically persist a validated fingerprint mapping."""
        self._validate(fingerprints)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {key: fingerprints[key] for key in sorted(fingerprints)},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"

        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self.path.parent,
            prefix=f".{self.path.name}.",
            delete=False,
        ) as temporary:
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)

        try:
            os.replace(temporary_path, self.path)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise

    def load(self) -> dict[str, str]:
        """Load persisted fingerprints; missing state means an initial build."""
        if not self.path.exists():
            return {}

        try:
            with self.path.open("r", encoding="utf-8") as handle:
                value = json.load(handle)
        except (OSError, json.JSONDecodeError) as error:
            raise IncrementalStateError(
                f"Unable to load GIR fingerprint state from '{self.path}'."
            ) from error

        if not isinstance(value, dict):
            raise IncrementalStateError(
                f"GIR fingerprint state at '{self.path}' must be a JSON object."
            )

        self._validate(value)
        return dict(value)

    @staticmethod
    def _validate(fingerprints: dict[str, str]) -> None:
        if not isinstance(fingerprints, dict):
            raise IncrementalStateError("GIR fingerprints must be a mapping.")
        for node_id, fingerprint in fingerprints.items():
            if not isinstance(node_id, str) or not isinstance(fingerprint, str):
                raise IncrementalStateError(
                    "GIR fingerprint state keys and values must be strings."
                )
