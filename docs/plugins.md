# ITL Plugin Guide — v1.0

Plugins are implementation extensions. They do not add new ITL source-language keywords or grammar.

## Plugin responsibilities

The implemented plugin architecture supports generation and validation capabilities selected by target/framework compatibility and the plugin manager.

A plugin may provide:

- generation behavior;
- validation behavior;
- framework/target metadata;
- compatibility information;
- integrity/trust metadata required by the plugin system.

## Trust boundary

Plugins execute with the privileges granted to the host process. ITL v1.0 does **not** claim a security sandbox for trusted Python plugins.

Only load plugins from sources you trust. Keep plugin dependencies and generated artifacts reviewable.

## Compatibility

Plugin compatibility is evaluated against the plugin API/compiler contracts implemented by the repository. A plugin should declare the target/framework capabilities it supports rather than assuming that every backend is compatible.

## Generation and validation

Generation plugins are invoked through the generation layer. Generated output is still subject to validation before emission. A validation failure must not be treated as successful output.

## Testing a plugin

The repository's plugin tests cover:

- discovery and registration;
- compatibility selection;
- generation integration;
- validation integration;
- integrity/trust failures;
- deterministic behavior.

Run the complete suite with:

```bash
python -m tests
```

## v1.0 limitation

There is no plugin declaration syntax in `.itl`. Plugins are configured through the implementation/tooling layer. Adding language-level plugin declarations would be a future language change and is outside the v1.0 release scope.
