# ITL Plugin System

Phase 11 adds a framework-neutral plugin boundary around the existing compiler and generation architecture.

## Architecture

The compiler remains responsible for language processing and normalized compiler information:

```text
.ITL source
→ Lexer
→ Parser
→ AST
→ Semantic Analysis
→ GIR
→ Dependency Graph
→ Change Detection
→ Diff Analysis
→ Build Plan
→ Scheduler
→ AI Generation
→ Validation
→ Emit
```

Plugins begin at the generation/validation boundary. They do not participate in lexing, parsing, semantic analysis, GIR construction, dependency analysis, change detection, or scheduling.

## Plugin contract

Every plugin exposes `PluginMetadata` and `configure(PluginConfig)`.

Metadata contains:

- `name`
- `version`
- `api_version`
- supported `targets`
- supported `frameworks`
- minimum/maximum compiler version
- declared capabilities

Capabilities are deliberately explicit. Current capability names used by the core are `generation` and `validation`. Installation and upgrade protocols are defined for future phases without implementing those behaviors now.

## Discovery and registration

`PluginRegistry` supports two standard-library discovery mechanisms:

1. **Module discovery** — a module exposes `plugin` or `create_plugin()`.
2. **Python entry-point discovery** — installed distributions may expose plugins through the `itl.plugins` entry-point group.

Registration validates the plugin contract and compiler compatibility before adding it to the registry.

Duplicate plugin names are rejected instead of silently replacing an existing implementation.

## Selection

Selection uses the normalized `GenerationContext` fields `target` and `framework`.

A plugin must match every constrained dimension declared by its metadata. A plugin that declares both target and framework receives a higher specificity score than a wildcard plugin. Equal best matches are rejected as ambiguous.

Missing matches raise `PluginNotFoundError`.

## Generation integration

Phase 10's `AIGenerator` already consumes a replaceable `GenerationProvider`. Phase 11 does not create a second generation pipeline.

`PluginGenerationProvider` is an adapter implementing the existing provider contract. It selects the plugin from the generation request and delegates generation to that plugin.

This means the existing flow remains:

```text
BuildPlan
→ BuildScheduler
→ AIGenerator
→ PluginGenerationProvider
→ selected plugin
```

The compiler core does not need React, Django, Flutter, or other framework-specific branches.

## Validation

`PluginManager.validate()` selects the same target/framework plugin and calls its validation hook when the plugin declares `validation` capability.

A plugin without validation capability returns a structured `SKIPPED` result. Plugin validation returns `PASSED` or `FAILED` with structured errors.

The reference plugin demonstrates this hook; a later validation/emission phase can place the hook into the broader pipeline without changing plugin contracts.

## Configuration

`PluginConfig` is an immutable, deterministic representation of configuration values. The registry passes configuration to the selected plugin through `configure()`.

Example:

```python
registry.configure(
    "react-reference",
    PluginConfig.from_mapping({"component_name": "Landing"}),
)
```

## Compatibility and failures

The plugin API is currently `1.0` and the compiler compatibility baseline is `1.0`.

The registry rejects:

- missing or invalid metadata
- missing `configure()`
- incompatible compiler versions
- duplicate plugin names
- ambiguous target/framework matches

Generation raises structured plugin capability/selection errors into the existing Phase 10 generation failure path rather than silently falling back to another plugin.

## Reference plugin

`itl.plugins.reference_react` is a minimal standard-library-only React reference plugin. It supports:

- target: `web`
- framework: `react`
- generation
- validation
- configuration of the generated component name

It is intentionally small. It proves the extension boundary without attempting to implement a complete React toolchain.

## Developing a plugin

A plugin module can follow this minimal structure:

```python
from itl.generation.models import GenerationRequest
from itl.generation.provider import ProviderResponse
from itl.plugins.models import PluginConfig, PluginMetadata


class MyPlugin:
    metadata = PluginMetadata(
        name="my-plugin",
        version="1.0.0",
        targets=("my-target",),
        frameworks=("my-framework",),
        capabilities=("generation",),
    )

    def configure(self, config: PluginConfig) -> None:
        self.config = config

    def generate(
        self,
        request: GenerationRequest,
        prompt: str,
    ) -> ProviderResponse:
        ...


plugin = MyPlugin()
```

Keep framework-specific rules, prompts, templates, output conventions, validation, installation, and upgrades inside the plugin. Do not add framework conditionals to the lexer, parser, analyzer, GIR, dependency graph, scheduler, or other compiler-core modules.

## Testing requirements

Plugin implementations should test:

- registration
- module discovery
- target/framework selection
- invalid plugins
- compiler incompatibility
- duplicate registration
- ambiguous selection
- missing plugins
- generation delegation
- validation behavior
- configuration

The repository's canonical standard-library test command remains:

```text
python -m tests
```
