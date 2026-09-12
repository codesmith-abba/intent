from __future__ import annotations

import os
import re
from pathlib import Path


class SecurityError(ValueError):
    """Raised when an operation violates an ITL security boundary."""


_SECRET_PATTERN = re.compile(
    r"(?i)(api[_-]?key|secret|password|token|authorization|bearer)\s*[:=]\s*([^\s,}]+)"
)


def ensure_within(root: str | Path, candidate: str | Path) -> Path:
    """Resolve candidate and require it to remain inside root."""
    root_path = Path(root).expanduser().resolve()
    candidate_path = Path(candidate)
    if not candidate_path.is_absolute():
        candidate_path = root_path / candidate_path
    resolved = candidate_path.resolve()
    try:
        resolved.relative_to(root_path)
    except ValueError as error:
        raise SecurityError(f"Path escapes security boundary: {candidate}") from error
    return resolved


def safe_relative_path(value: str) -> str:
    """Validate a relative filesystem member name."""
    path = Path(value)
    if not value or path.is_absolute() or any(part == ".." for part in path.parts):
        raise SecurityError(f"Unsafe relative path: {value!r}")
    if "\x00" in value:
        raise SecurityError("NUL bytes are not allowed in paths.")
    return path.as_posix()


def contains_secret_like_value(text: str) -> bool:
    """Return true when text resembles a credential-bearing key/value pair."""
    return _SECRET_PATTERN.search(text) is not None


def redact_secret(text: str) -> str:
    """Redact common secret-like key/value material before user-visible output."""
    return _SECRET_PATTERN.sub(lambda match: f"{match.group(1)}=<redacted>", text)


def is_secret_environment_name(name: str) -> bool:
    upper = name.upper()
    return any(marker in upper for marker in ("KEY", "SECRET", "TOKEN", "PASSWORD", "CREDENTIAL"))


def filtered_environment() -> dict[str, str]:
    """Return an environment suitable for child processes without obvious secrets."""
    return {key: value for key, value in os.environ.items() if not is_secret_environment_name(key)}
