from itl.generation.models import GenerationRequest
from itl.generation.provider import ProviderResponse
from itl.plugins.models import (
    PluginConfig,
    PluginMetadata,
    PluginValidationResult,
    PluginValidationStatus,
)


class ReactReferencePlugin:
    """Minimal React plugin proving the framework boundary without external APIs."""

    metadata = PluginMetadata(
        name="react-reference",
        version="1.0.0",
        targets=("web",),
        frameworks=("react",),
        capabilities=("generation", "validation"),
    )

    def __init__(self) -> None:
        self._config = PluginConfig()

    def configure(self, config: PluginConfig) -> None:
        self._config = config

    def generate(
        self,
        request: GenerationRequest,
        prompt: str,
    ) -> ProviderResponse:
        component_name = self._component_name(request.requested_unit)
        text = request.context.intent or request.context.unit_id
        output = (
            f"export default function {component_name}() {{\n"
            f"  return <div>{text}</div>;\n"
            f"}}\n"
        )
        return ProviderResponse(
            output=output,
            provider=self.metadata.name,
            model="reference",
            metadata={"framework": "react"},
        )

    def validate(
        self,
        request: GenerationRequest,
        output: str,
    ) -> PluginValidationResult:
        if "export default function " not in output:
            return PluginValidationResult(
                status=PluginValidationStatus.FAILED,
                errors=("Reference React output is missing a default component.",),
            )
        return PluginValidationResult(
            status=PluginValidationStatus.PASSED,
        )

    def _component_name(self, unit_id: str) -> str:
        configured = self._config.get("component_name")
        if configured:
            return str(configured)
        pieces = [piece for piece in unit_id.replace("/", " ").replace("-", " ").split() if piece]
        return "".join(piece[:1].upper() + piece[1:] for piece in pieces) or "IntentComponent"


def create_plugin() -> ReactReferencePlugin:
    return ReactReferencePlugin()


plugin = create_plugin()
