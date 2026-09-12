# ITL Phase 22 — Security Hardening

Phase 22 establishes secure defaults around untrusted ITL projects, generated files, packages, plugins, local AI providers, and persistent state.

## Threat model

ITL may process projects obtained from untrusted or partially trusted sources. The important attacker-controlled inputs are:

- `.itl` source and import names
- project state and cache files
- package archives and package manifests
- plugin packages and plugin entry points after explicit trust
- AI endpoint configuration and AI responses
- names that become generated filenames or code identifiers

The compiler is expected to be usable without AI and without executing generated application code.

## Security boundaries

### Source and imports

ITL source loading is confined to the discovered project root. Relative traversal (`..`), absolute paths, non-`.itl` imports, and symlink escapes are rejected through resolved-path containment checks.

### Project state and writes

Project entrypoints must be relative `.itl` paths and may not escape the project. Project state continues to use atomic replacement when written. Generated build artifacts remain under `.project`.

### Generated code and subprocesses

The React backend no longer installs packages or starts a development server by default. `itl dev` generates the project without executing external commands.

External execution is explicit:

```text
itl dev <project> --install
itl dev <project> --install --allow-install-scripts
itl dev <project> --run
```

`npm install` uses `--ignore-scripts` unless lifecycle scripts are explicitly enabled. This prevents package lifecycle hooks from becoming an implicit code-execution path.

### Packages

Package archives are verified before extraction and archive member paths are constrained to safe relative paths. Installed package names and versions are constrained to filesystem-safe identifiers. Installed-state paths must remain inside the package cache. Plugin code is not loaded until the package has been explicitly trusted and its integrity has been re-verified.

### Plugins

Plugin discovery remains an explicit operation. Package-installed plugins require explicit trust. Compatibility, metadata, capabilities, and package integrity are checked before registration.

A trusted plugin is executable code by design; ITL does not claim that an in-process Python plugin is sandboxed. Deployments requiring a hostile-plugin boundary should run plugins in an OS/container sandbox.

### AI providers

The local AI provider defaults to loopback endpoints only. Remote endpoints require explicit `allow_remote_endpoint=True`. API keys remain configuration values and are not written into generated project artifacts by the provider.

AI remains a replaceable backend capability. The compiler does not require AI to parse, analyze, or compile ITL.

### Secrets

`.itl` source should not contain credentials. User-visible security errors should avoid echoing obvious secret-like key/value pairs. `redact_secret()` is available for CLI-facing error handling and diagnostics.

### Cache and state

Cache persistence now uses atomic replacement and rejects malformed top-level cache structures instead of continuing with corrupted state. Project state already uses temporary-file replacement and remains validated on load/save.

## Residual risks

- A trusted Python plugin can execute arbitrary code with the permissions of the ITL process.
- `--allow-install-scripts` intentionally permits package lifecycle code execution and should only be used for trusted dependencies.
- `--run` intentionally starts generated development code.
- Remote AI endpoints are explicitly supported when opted into; network privacy then depends on that endpoint.
- Resource exhaustion (very large source files, archives, or generated projects) is not fully sandboxed in this phase.

## Security principle

ITL should treat source, packages, generated artifacts, and external integrations as separate capability boundaries. The default path should parse and generate safely; privileged actions should require an explicit opt-in.
