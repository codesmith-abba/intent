from collections.abc import Mapping

from itl.build.models import BuildItem
from itl.cache.cache import Cache
from itl.generation.models import GenerationContext, GenerationRequest, GenerationResult, GenerationStatus
from itl.generation.prompt import GenerationPromptBuilder
from itl.generation.provider import GenerationProvider
from itl.security import contains_secret_like_value, redact_secret


class GenerationFailure(RuntimeError):
    """Structured generation failure raised into the existing build executor."""

    def __init__(self, result: GenerationResult):
        self.result = result
        super().__init__(redact_secret(result.error or "Generation failed."))


class AIGenerator:
    """Compiler generation backend for scheduled logical build units."""

    def __init__(
        self,
        provider: GenerationProvider,
        contexts: Mapping[str, GenerationContext],
        cache: Cache | None = None,
        prompt_builder: GenerationPromptBuilder | None = None,
    ):
        self.provider = provider
        self.contexts = contexts
        self.cache = cache
        self.prompt_builder = prompt_builder or GenerationPromptBuilder()

    def request_for(self, item: BuildItem) -> GenerationRequest:
        try:
            context = self.contexts[item.source]
        except KeyError as error:
            raise GenerationFailure(
                GenerationResult(
                    unit_id=item.source,
                    status=GenerationStatus.FAILED,
                    error=f"No generation context exists for '{item.source}'.",
                )
            ) from error
        return GenerationRequest(context=context, requested_unit=item.source)

    def generate(self, item: BuildItem) -> GenerationResult:
        request = self.request_for(item)
        if self.cache is not None:
            entry = self.cache.get(item.source)
            if entry is not None and entry.output is not None:
                metadata = dict(entry.metadata)
                return GenerationResult(
                    unit_id=item.source,
                    status=GenerationStatus.CACHED,
                    output=entry.output,
                    provider=metadata.get("provider"),
                    model=metadata.get("model"),
                    metadata=metadata,
                )

        prompt = self.prompt_builder.build(request)
        try:
            response = self.provider.generate(request, prompt)
        except Exception as error:
            return GenerationResult(
                unit_id=item.source,
                status=GenerationStatus.FAILED,
                error=redact_secret(str(error)),
            )

        result = GenerationResult(
            unit_id=item.source,
            status=GenerationStatus.SUCCESS,
            output=response.output,
            provider=response.provider,
            model=response.model,
            metadata=dict(response.metadata),
        )

        # Do not persist output that resembles credential-bearing key/value data.
        # The generated result is still returned to the caller for explicit handling.
        if self.cache is not None and result.output is not None and not contains_secret_like_value(result.output):
            metadata = dict(result.metadata)
            metadata.update({"provider": result.provider, "model": result.model})
            self.cache.put(item.source, output=result.output, metadata=metadata)
            self.cache.save()

        return result

    def build(self, item: BuildItem) -> str:
        result = self.generate(item)
        if result.status == GenerationStatus.FAILED:
            raise GenerationFailure(result)
        return result.output or ""

    def prompt_for(self, item: BuildItem) -> str:
        return self.prompt_builder.build(self.request_for(item))
