from __future__ import annotations

import hashlib
from importlib.resources import files
from pathlib import Path

import itl


def test_release_version_is_stable():
    assert itl.__version__ == "1.0.0"


def test_packaged_browser_runtime_matches_repository_runtime():
    packaged = files("itl.runtime").joinpath("browser.js").read_bytes()
    repository_runtime = (Path(__file__).resolve().parents[1] / "runtime" / "browser.js").read_bytes()

    assert hashlib.sha256(packaged).digest() == hashlib.sha256(repository_runtime).digest()
