# ITL Local AI Runtime

ITL can use a local AI model through the existing `GenerationProvider` boundary. The compiler does not require AI to compile or analyze an ITL program; local generation is an optional backend capability.

The current implementation uses an **OpenAI-compatible HTTP chat-completions endpoint** and Python's standard library only. No model SDK or cloud service is required.

## 1. Local setup

Run an OpenAI-compatible local inference server on your machine. For example, an Ollama installation can expose its OpenAI-compatible API locally.

Then select the endpoint and model in Python:

```python
from itl.generation import LocalAIProvider, LocalProviderConfig

provider = LocalAIProvider(
    LocalProviderConfig(
        endpoint="http://127.0.0.1:11434/v1/chat/completions",
        model="llama3.2",
        timeout=120.0,
    )
)
```

The default endpoint is `http://127.0.0.1:11434/v1/chat/completions` and the default model name is `llama3.2`.

The endpoint must implement the OpenAI-compatible shape:

```json
{
  "choices": [
    {
      "message": {
        "content": "generated text"
      }
    }
  ]
}
```

A completion request contains the configured model and a single user message containing the deterministic ITL generation prompt.

## 2. Configuration

`LocalProviderConfig` supports:

- `endpoint` — local or private OpenAI-compatible HTTP(S) endpoint.
- `model` — model identifier understood by the local server.
- `timeout` — request timeout in seconds.
- `api_key` — optional bearer token for local/private servers that require one.
- `temperature` — optional sampling temperature.
- `max_tokens` — optional output limit.

The provider does not discover, download, or manage models. Model lifecycle remains the responsibility of the local inference server.

## 3. Streaming

`LocalAIProvider.generate_stream()` supports OpenAI-compatible Server-Sent Events (SSE) and yields text deltas as they arrive:

```python
for chunk in provider.generate_stream(request, prompt):
    print(chunk, end="", flush=True)
```

Streaming is an optional provider capability. The core `GenerationProvider` interface remains unchanged, so existing compiler code only depends on `generate()`.

## 4. Privacy and offline behavior

When the configured endpoint is local, prompts and generated output remain on the local machine and do not need to leave the device.

ITL's local provider has no cloud SDK dependency and performs no automatic cloud fallback. If the local endpoint is unavailable, generation fails instead of silently switching providers.

Offline operation therefore works when:

1. the local model is already installed;
2. the local inference server is running; and
3. the machine has no network access.

If the model server itself needs to download a model, that download is outside ITL and normally requires network access once during setup.

## 5. Errors and timeouts

The provider exposes structured exceptions:

- `LocalProviderError` — general local provider failure.
- `LocalProviderTimeout` — request exceeded the configured timeout.
- `LocalProviderHTTPError` — the endpoint returned an HTTP error.

The existing `AIGenerator` catches provider exceptions and converts them into `GenerationResult(status=FAILED, ...)`. The compiler pipeline itself remains usable without an AI provider.

## 6. Deterministic testing

Use `FakeGenerationProvider` when a test should never perform network or model inference:

```python
from itl.generation import FakeGenerationProvider

provider = FakeGenerationProvider(output="expected output")
```

The fake provider records calls and always returns the configured output, making compiler/provider integration tests deterministic and fast.

## 7. Architecture boundary

The dependency direction is:

```text
ITL compiler / generation backend
              |
              v
     GenerationProvider
          /       \
         /         \
       Fake       LocalAIProvider
                    |
                    v
          local inference server
                    |
                    v
                local model
```

Compiler stages do not import a model SDK or know which local model is being used. A future provider can implement the same interface without changing the lexer, parser, analyzer, GIR, or compiler pipeline.

## 8. Limitations

- The current local provider targets OpenAI-compatible chat-completions APIs; provider-specific APIs are not implemented directly.
- Model quality, context limits, hardware requirements, and generation speed depend on the selected local model/server.
- Streaming currently supports SSE responses with OpenAI-compatible `choices[].delta.content` chunks.
- There is no automatic model installation or model discovery.
- The provider does not add retry or failover behavior; failures are explicit so offline operation remains predictable.
