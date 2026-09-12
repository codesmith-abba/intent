import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from itl.generation.fake import FakeGenerationProvider
from itl.generation.local import LocalAIProvider, LocalProviderConfig, LocalProviderTimeout
from itl.generation.models import GenerationContext, GenerationRequest


def _request() -> GenerationRequest:
    return GenerationRequest(
        context=GenerationContext(unit_id="home", unit_type="Page"),
        requested_unit="home",
    )


def test_fake_provider_is_deterministic_and_records_prompt():
    provider = FakeGenerationProvider(output="stable")
    request = _request()

    first = provider.generate(request, "prompt")
    second = provider.generate(request, "prompt")

    assert first.output == "stable"
    assert second.output == first.output
    assert first.provider == "fake"
    assert len(provider.calls) == 2
    assert provider.calls[0][1] == "prompt"


def test_local_provider_posts_openai_compatible_request():
    received = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            received["path"] = self.path
            received["body"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            payload = {"choices": [{"message": {"content": "local output"}}]}
            raw = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        config = LocalProviderConfig(
            endpoint=f"http://127.0.0.1:{server.server_port}/v1/chat/completions",
            model="test-model",
            temperature=0.0,
            max_tokens=32,
        )
        response = LocalAIProvider(config).generate(_request(), "hello")
    finally:
        server.shutdown()
        thread.join()
        server.server_close()

    assert response.output == "local output"
    assert response.provider == "local"
    assert response.model == "test-model"
    assert received["path"] == "/v1/chat/completions"
    assert received["body"]["model"] == "test-model"
    assert received["body"]["messages"] == [{"role": "user", "content": "hello"}]
    assert received["body"]["temperature"] == 0.0
    assert received["body"]["max_tokens"] == 32
    assert received["body"]["stream"] is False


def test_local_provider_streams_sse_deltas():
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            chunks = [
                {"choices": [{"delta": {"content": "hello"}}]},
                {"choices": [{"delta": {"content": " world"}}]},
            ]
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for chunk in chunks:
                self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        config = LocalProviderConfig(
            endpoint=f"http://127.0.0.1:{server.server_port}/v1/chat/completions"
        )
        output = "".join(LocalAIProvider(config).generate_stream(_request(), "hello"))
    finally:
        server.shutdown()
        thread.join()
        server.server_close()

    assert output == "hello world"


def test_local_provider_reports_unreachable_endpoint():
    config = LocalProviderConfig(
        endpoint="http://127.0.0.1:1/v1/chat/completions",
        timeout=0.05,
    )
    try:
        LocalAIProvider(config).generate(_request(), "hello")
    except LocalProviderTimeout:
        raise AssertionError("port refusal should not be reported as a timeout")
    except Exception as error:
        assert "Unable to reach local AI endpoint" in str(error)
    else:
        raise AssertionError("expected local endpoint failure")
