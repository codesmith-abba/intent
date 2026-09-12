"""Local OpenAI-compatible AI generation provider.

The provider intentionally depends only on Python's standard library so local
AI generation can run offline without adding a model SDK to the compiler.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from itl.generation.models import GenerationRequest
from itl.generation.provider import ProviderResponse


class LocalProviderError(RuntimeError):
    """Base error for local provider failures."""


class LocalProviderTimeout(LocalProviderError):
    """Raised when the local endpoint does not respond before the timeout."""


class LocalProviderHTTPError(LocalProviderError):
    """Raised when the local endpoint returns an HTTP error."""


@dataclass(frozen=True, slots=True)
class LocalProviderConfig:
    """Configuration for an OpenAI-compatible local inference endpoint."""

    endpoint: str = "http://127.0.0.1:11434/v1/chat/completions"
    model: str = "llama3.2"
    timeout: float = 120.0
    api_key: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None

    def __post_init__(self) -> None:
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        if not self.endpoint.startswith(("http://", "https://")):
            raise ValueError("endpoint must be an HTTP(S) URL")
        if not self.model.strip():
            raise ValueError("model must not be empty")


class LocalAIProvider:
    """GenerationProvider implementation for local OpenAI-compatible servers."""

    name = "local"

    def __init__(self, config: LocalProviderConfig | None = None):
        self.config = config or LocalProviderConfig()

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def _payload(self, prompt: str, *, stream: bool = False) -> dict[str, object]:
        payload: dict[str, object] = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": stream,
        }
        if self.config.temperature is not None:
            payload["temperature"] = self.config.temperature
        if self.config.max_tokens is not None:
            payload["max_tokens"] = self.config.max_tokens
        return payload

    def _request(self, prompt: str, *, stream: bool = False) -> Request:
        body = json.dumps(self._payload(prompt, stream=stream)).encode("utf-8")
        return Request(
            self.config.endpoint,
            data=body,
            headers=self._headers(),
            method="POST",
        )

    @staticmethod
    def _extract_output(data: dict[str, object]) -> str:
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise LocalProviderError("Local endpoint response contains no choices")

        choice = choices[0]
        if not isinstance(choice, dict):
            raise LocalProviderError("Local endpoint returned an invalid choice")

        message = choice.get("message")
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            return message["content"]

        text = choice.get("text")
        if isinstance(text, str):
            return text

        raise LocalProviderError("Local endpoint response contains no text output")

    def generate(self, request: GenerationRequest, prompt: str) -> ProviderResponse:
        """Generate one complete response through the configured local endpoint."""
        del request  # The stable provider boundary supplies prompt + metadata.
        try:
            with urlopen(self._request(prompt), timeout=self.config.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except TimeoutError as error:
            raise LocalProviderTimeout("Local AI request timed out") from error
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise LocalProviderHTTPError(
                f"Local AI endpoint returned HTTP {error.code}: {detail[:500]}"
            ) from error
        except URLError as error:
            raise LocalProviderError(f"Unable to reach local AI endpoint: {error.reason}") from error
        except json.JSONDecodeError as error:
            raise LocalProviderError("Local AI endpoint returned invalid JSON") from error

        if not isinstance(data, dict):
            raise LocalProviderError("Local AI endpoint returned an invalid response")

        return ProviderResponse(
            output=self._extract_output(data),
            provider=self.name,
            model=self.config.model,
            metadata={"endpoint": self.config.endpoint},
        )

    def generate_stream(self, request: GenerationRequest, prompt: str) -> Iterator[str]:
        """Yield text deltas from an OpenAI-compatible SSE streaming endpoint."""
        del request
        try:
            response = urlopen(self._request(prompt, stream=True), timeout=self.config.timeout)
        except TimeoutError as error:
            raise LocalProviderTimeout("Local AI streaming request timed out") from error
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise LocalProviderHTTPError(
                f"Local AI endpoint returned HTTP {error.code}: {detail[:500]}"
            ) from error
        except URLError as error:
            raise LocalProviderError(f"Unable to reach local AI endpoint: {error.reason}") from error

        try:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError as error:
                    raise LocalProviderError("Local AI stream returned invalid JSON") from error
                choices = data.get("choices", [])
                if not isinstance(choices, list) or not choices:
                    continue
                choice = choices[0]
                if not isinstance(choice, dict):
                    continue
                delta = choice.get("delta")
                if isinstance(delta, dict) and isinstance(delta.get("content"), str):
                    yield delta["content"]
        finally:
            response.close()
