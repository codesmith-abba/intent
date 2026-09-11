import tempfile
from pathlib import Path

from itl.build.executor import BuildExecutor
from itl.build.models import BuildItem, BuildPlan
from itl.cache.cache import Cache
from itl.cache.decision import CacheStatus
from itl.generation.generator import AIGenerator
from itl.generation.models import (
    GenerationContext,
    GenerationRequest,
    GenerationStatus,
)
from itl.generation.prompt import GenerationPromptBuilder
from itl.generation.provider import ProviderResponse
from itl.gir.models import GIRPage


class FakeProvider:
    def __init__(self, output="generated"):
        self.output = output
        self.calls = []
        self.fail = False

    def generate(self, request, prompt):
        self.calls.append((request, prompt))
        if self.fail:
            raise RuntimeError("provider unavailable")
        return ProviderResponse(
            output=self.output,
            provider="fake",
            model="fake-model",
            metadata={"test": True},
        )


def test_generation_context_from_gir():
    page = GIRPage(
        intent="Build a storefront",
        name="home",
        theme="light",
    )
    context = GenerationContext.from_gir(
        "home",
        page,
        dependencies={"layout"},
    )

    assert context.unit_id == "home"
    assert context.unit_type == "GIRPage"
    assert context.intent == "Build a storefront"
    assert context.dependencies == ("layout",)


def test_prompt_is_deterministic_and_structured():
    context = GenerationContext(
        unit_id="home",
        unit_type="GIRPage",
        intent="Build a storefront",
        constraints=("responsive", "accessible"),
        dependencies=("header",),
        target="web",
        framework="react",
        existing_output="old output",
    )
    request = GenerationRequest(
        context=context,
        requested_unit="home",
    )
    builder = GenerationPromptBuilder()

    first = builder.build(request)
    second = builder.build(request)

    assert first == second
    assert "Build a storefront" in first
    assert "responsive" in first
    assert "header" in first
    assert "web" in first
    assert "react" in first
    assert "old output" in first
    assert "ITL SOURCE" not in first


def test_successful_generation():
    provider = FakeProvider()
    generator = AIGenerator(
        provider,
        {"home": GenerationContext("home", "GIRPage", intent="Home")},
    )
    item = BuildItem("home", CacheStatus.MISS)

    result = generator.generate(item)

    assert result.status == GenerationStatus.SUCCESS
    assert result.output == "generated"
    assert result.provider == "fake"
    assert len(provider.calls) == 1


def test_provider_failure_is_structured():
    provider = FakeProvider()
    provider.fail = True
    generator = AIGenerator(
        provider,
        {"home": GenerationContext("home", "GIRPage")},
    )

    result = generator.generate(BuildItem("home", CacheStatus.MISS))

    assert result.status == GenerationStatus.FAILED
    assert result.error == "provider unavailable"


def test_cache_interaction_avoids_provider_call():
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "home.itl"
        source.write_text("app $home", encoding="utf-8")
        cache = Cache(directory)
        cache.put(str(source), output="cached output", metadata={"provider": "fake"})
        cache.save()

        provider = FakeProvider()
        generator = AIGenerator(
            provider,
            {str(source): GenerationContext(str(source), "GIRPage")},
            cache=cache,
        )

        result = generator.generate(BuildItem(str(source), CacheStatus.HIT))

        assert result.status == GenerationStatus.CACHED
        assert result.output == "cached output"
        assert provider.calls == []


def test_incremental_generation_only_executes_scheduled_items():
    provider = FakeProvider()
    generator = AIGenerator(
        provider,
        {
            "changed": GenerationContext("changed", "GIRPage"),
            "unchanged": GenerationContext("unchanged", "GIRPage"),
        },
    )
    executor = BuildExecutor(generator.build)
    plan = BuildPlan(
        items=[BuildItem("changed", CacheStatus.INVALIDATED)],
    )

    results = executor.execute(plan)

    assert results.succeeded
    assert [call[0].requested_unit for call in provider.calls] == ["changed"]


def test_scheduler_dependency_order_reaches_generation_provider():
    provider = FakeProvider()
    generator = AIGenerator(
        provider,
        {
            "base": GenerationContext("base", "GIRPage"),
            "child": GenerationContext("child", "GIRSection", dependencies=("base",)),
        },
    )
    executor = BuildExecutor(generator.build)
    plan = BuildPlan(
        items=[
            BuildItem("child", CacheStatus.MISS, {"base"}),
            BuildItem("base", CacheStatus.MISS),
        ]
    )

    results = executor.execute(plan)

    assert results.succeeded
    assert [call[0].requested_unit for call in provider.calls] == ["base", "child"]
