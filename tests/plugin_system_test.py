from dataclasses import dataclass

from itl.build.models import BuildItem
from itl.cache.decision import CacheStatus
from itl.generation.generator import AIGenerator
from itl.generation.models import GenerationContext, GenerationRequest
from itl.generation.provider import ProviderResponse
from itl.plugins import (
    DuplicatePluginError,
    IncompatiblePluginError,
    InvalidPluginError,
    PluginConfig,
    PluginMetadata,
    PluginNotFoundError,
    PluginRegistry,
    PluginSelectionError,
    PluginValidationStatus,
)
from itl.plugins.reference_react import ReactReferencePlugin


def _request(
    target: str = "web",
    framework: str = "react",
    unit_id: str = "home",
) -> GenerationRequest:
    return GenerationRequest(
        context=GenerationContext(
            unit_id=unit_id,
            unit_type="GIRPage",
            intent="Build the home page",
            target=target,
            framework=framework,
        ),
        requested_unit=unit_id,
    )


def test_plugin_registration_and_listing():
    registry = PluginRegistry()
    plugin = ReactReferencePlugin()

    registry.register(plugin)

    assert registry.plugins == (plugin,)


def test_plugin_discovery_from_module():
    registry = PluginRegistry()

    discovered = registry.discover(("itl.plugins.reference_react",))

    assert len(discovered) == 1
    assert discovered[0].metadata.name == "react-reference"


def test_plugin_selection_by_target_and_framework():
    registry = PluginRegistry()
    registry.register(ReactReferencePlugin())

    selected = registry.select("web", "react")

    assert selected.metadata.name == "react-reference"


def test_invalid_plugin_is_rejected():
    class InvalidPlugin:
        pass

    registry = PluginRegistry()

    try:
        registry.register(InvalidPlugin())
    except InvalidPluginError:
        return
    raise AssertionError("Invalid plugin was accepted")


def test_incompatible_plugin_is_rejected():
    class FuturePlugin:
        metadata = PluginMetadata(
            name="future",
            version="1.0.0",
            min_compiler_version="2.0",
        )

        def configure(self, config):
            pass

    registry = PluginRegistry(compiler_version="1.0")

    try:
        registry.register(FuturePlugin())
    except IncompatiblePluginError:
        return
    raise AssertionError("Incompatible plugin was accepted")


def test_duplicate_plugin_is_rejected():
    registry = PluginRegistry()
    registry.register(ReactReferencePlugin())

    try:
        registry.register(ReactReferencePlugin())
    except DuplicatePluginError:
        return
    raise AssertionError("Duplicate plugin was accepted")


def test_ambiguous_plugin_selection_is_rejected():
    class FirstPlugin(ReactReferencePlugin):
        metadata = PluginMetadata(
            name="first",
            version="1.0.0",
            targets=("web",),
            frameworks=("react",),
        )

    class SecondPlugin(ReactReferencePlugin):
        metadata = PluginMetadata(
            name="second",
            version="1.0.0",
            targets=("web",),
            frameworks=("react",),
        )

    registry = PluginRegistry()
    registry.register(FirstPlugin())
    registry.register(SecondPlugin())

    try:
        registry.select("web", "react")
    except PluginSelectionError:
        return
    raise AssertionError("Ambiguous plugin selection was accepted")


def test_missing_plugin_is_reported():
    registry = PluginRegistry()

    try:
        registry.select("mobile", "flutter")
    except PluginNotFoundError:
        return
    raise AssertionError("Missing plugin did not raise")


def test_reference_plugin_generation():
    plugin = ReactReferencePlugin()
    response = plugin.generate(_request(), "ignored prompt")

    assert response.provider == "react-reference"
    assert "export default function Home" in response.output


def test_reference_plugin_validation_hook():
    plugin = ReactReferencePlugin()
    request = _request()

    valid = plugin.validate(request, "export default function Home() {}")
    invalid = plugin.validate(request, "const value = 1;")

    assert valid.status == PluginValidationStatus.PASSED
    assert invalid.status == PluginValidationStatus.FAILED
    assert invalid.errors


def test_plugin_configuration_reaches_reference_plugin():
    registry = PluginRegistry()
    plugin = ReactReferencePlugin()
    registry.register(plugin)
    registry.configure(
        "react-reference",
        PluginConfig.from_mapping({"component_name": "Landing"}),
    )

    response = plugin.generate(_request(), "ignored prompt")

    assert "export default function Landing" in response.output


def test_plugin_generation_integrates_with_ai_generator():
    registry = PluginRegistry()
    registry.register(ReactReferencePlugin())
    generator = AIGenerator(
        provider=registry.generation_provider(),
        contexts={
            "home": _request().context,
        },
    )

    result = generator.generate(
        BuildItem(source="home", status=CacheStatus.MISS),
    )

    assert result.output is not None
    assert result.provider == "react-reference"
    assert result.status.value == "success"


def test_plugin_manager_validation_selects_same_plugin():
    registry = PluginRegistry()
    registry.register(ReactReferencePlugin())
    request = _request()

    result = registry_manager_validate(registry, request, "const invalid = true;")

    assert result.status == PluginValidationStatus.FAILED


def test_plugin_without_validation_capability_is_skipped():
    class GenerationOnlyPlugin(ReactReferencePlugin):
        metadata = PluginMetadata(
            name="generation-only",
            version="1.0.0",
            targets=("web",),
            frameworks=("react",),
            capabilities=("generation",),
        )

    registry = PluginRegistry()
    registry.register(GenerationOnlyPlugin())

    result = registry_manager_validate(registry, _request(), "anything")

    assert result.status == PluginValidationStatus.SKIPPED


def registry_manager_validate(registry, request, output):
    from itl.plugins import PluginManager

    return PluginManager(registry).validate(request, output)
