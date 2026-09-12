import tempfile
from pathlib import Path

from itl.compiler.loader import ProjectLoader
from itl.generation.local import LocalProviderConfig
from itl.security import SecurityError, contains_secret_like_value, ensure_within, redact_secret


def test_ensure_within_rejects_path_traversal():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        try:
            ensure_within(root, root / ".." / "outside.txt")
        except SecurityError:
            return
    raise AssertionError("path traversal was accepted")


def test_project_loader_rejects_import_path_escape():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "app.itl").write_text("app $Demo {}", encoding="utf-8")
        loader = ProjectLoader(root)
        try:
            loader.load_file("../outside.itl")
        except SecurityError:
            return
    raise AssertionError("import traversal was accepted")


def test_local_provider_rejects_remote_endpoint_by_default():
    try:
        LocalProviderConfig(endpoint="https://example.com/v1/chat/completions")
    except ValueError:
        return
    raise AssertionError("remote AI endpoint was accepted by default")


def test_local_provider_allows_explicit_remote_opt_in():
    config = LocalProviderConfig(
        endpoint="https://example.com/v1/chat/completions",
        allow_remote_endpoint=True,
    )
    assert config.endpoint.startswith("https://")


def test_secret_detection_and_redaction():
    value = "api_key=super-secret token=abc"
    assert contains_secret_like_value(value)
    assert redact_secret(value) == "api_key=<redacted> token=<redacted>"
