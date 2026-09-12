# ITL Phase 20 — Package and Plugin Registry

Phase 20 introduces a local, file-backed package distribution mechanism for the existing ITL plugin contracts.

## Design boundary

The package layer sits outside the compiler language pipeline:

```text
.itl
→ Lexer
→ Parser
→ Analyzer
→ GIR
→ Build / Generation / Validation
→ PluginRegistry
                     ↑
              PackageManager
                     ↑
              Local .itlpkg registry
```

The package system does not replace `PluginRegistry`, `PluginMetadata`, `ITLPlugin`, `GenerationPlugin`, or `ValidationPlugin`. A plugin loaded from a package must still pass the existing `PluginRegistry.register()` contract and compatibility checks.

## Package format

An ITL package is a ZIP archive with the extension `.itlpkg`.

Required member:

```text
manifest.json
```

The manifest contains:

```json
{
  "format_version": "1.0",
  "name": "example-plugin",
  "version": "1.0.0",
  "type": "plugin",
  "plugin": {
    "name": "example-plugin",
    "version": "1.0.0",
    "api_version": "1.0",
    "targets": ["web"],
    "frameworks": ["react"],
    "min_compiler_version": "1.0",
    "max_compiler_version": null,
    "capabilities": ["generation"]
  },
  "dependencies": [
    {"name": "shared-plugin", "constraint": ">=1.0,<2.0"}
  ],
  "entry_point": {
    "module": "example_plugin",
    "attribute": "plugin"
  },
  "files": {
    "example_plugin.py": "<sha256>"
  },
  "metadata": {}
}
```

`files` contains SHA-256 hashes for every payload file. The manifest itself is not listed as a payload file; the complete archive hash is stored in installed state as an additional integrity check.

Package paths are normalized and traversal paths such as `../x` or absolute paths are rejected.

## Versioning and dependencies

Package versions use numeric semantic versions such as `1.2.3`.

Supported dependency constraints include:

- `*`
- exact versions such as `1.2.3`
- `>=`, `<=`, `>`, `<`
- combined constraints such as `>=1.0,<2.0`
- caret ranges such as `^1.2`
- tilde ranges such as `~1.2`

`PackageResolver` searches the local registry deterministically and selects the highest compatible version. Dependencies are resolved recursively. Unsatisfiable dependency graphs are rejected rather than partially installed.

Plugin packages also inherit the existing plugin API and compiler compatibility rules. A package whose plugin metadata requires an incompatible compiler is not resolved.

## Local registry

`LocalPackageRegistry` scans a directory for `.itlpkg` files.

No network registry is required in Phase 20. A future remote registry can implement the same package metadata/resolution boundary without changing plugin contracts.

Example:

```python
from itl.packages import LocalPackageRegistry

registry = LocalPackageRegistry("./packages")
resolved = registry.resolve("example-plugin", ">=1.0,<2.0")
```

Registry discovery verifies package integrity before a package becomes a resolution candidate. Package code is never imported during discovery or resolution.

## Installation and cache

`PackageManager` installs verified packages into a local cache:

```text
<cache>/
├── state.json
└── <package-name>/
    └── <version>/
        ├── manifest.json
        ├── package.itlpkg
        └── <payload files>
```

Installation:

1. verifies the source archive
2. resolves dependencies
3. installs dependencies first
4. extracts only verified files
5. stores the original archive and archive SHA-256
6. records installed metadata
7. marks the package **untrusted**

An already-installed identical archive is reused; different contents under the same package/version are rejected.

## Upgrade

`PackageManager.upgrade(name)` selects a newer compatible package from the local registry. Installed dependency constraints are checked before the upgrade is accepted.

An upgrade is a new package version and is not automatically trusted.

## Removal

A package cannot be removed while another installed package declares a dependency on that package version. This prevents silently breaking an installed dependency graph.

## Integrity verification

Two integrity layers are used:

1. **Archive SHA-256** — detects replacement/corruption of the installed `.itlpkg` archive.
2. **Payload SHA-256** — detects changes to extracted package files.

`PackageManager.verify()` checks both layers plus manifest consistency.

Integrity is not publisher authentication. SHA-256 proves that the verified bytes have not changed; it does not prove who created them. Publisher signatures/key infrastructure is deliberately not invented in Phase 20.

## Security and trust model

The critical rule is:

> **Installing a package does not execute plugin code.**

Every installed package starts as `trusted=False`.

`PackageManager.load_plugin()` refuses to import code until the user explicitly calls:

```python
manager.trust("example-plugin")
```

Trust is also conditional on a successful integrity verification immediately before loading.

Only after those checks does the package directory become an import location and the declared entry point get imported. The resulting object is then passed through the existing `PluginRegistry.register()` contract.

This creates three separate stages:

```text
Package file
    ↓ verify
Installed / untrusted
    ↓ explicit trust + verify
Executable / trusted
    ↓ existing PluginRegistry contract
Active plugin
```

No downloaded package is automatically executed during discovery, resolution, installation, or upgrade.

## Plugin contract preservation

A packaged plugin must still provide the existing `PluginMetadata` and `configure()` contract. Generation/validation capabilities remain declared by plugin metadata and are enforced by the existing `PluginRegistry` and `PluginManager`.

The package layer therefore distributes plugins; it does not redefine what an ITL plugin is.

## API

Main public objects:

- `PackageManifest`
- `PackageDependency`
- `PackageBuilder`
- `PackageReader`
- `LocalPackageRegistry`
- `PackageResolver`
- `PackageManager`
- `InstalledPackage`

The implementation uses only the Python standard library.

## Tests

Phase 20 tests are in:

```text
tests/package_registry_test.py
```

They cover:

- version constraints
- dependency resolution
- highest compatible dependency selection
- compiler/plugin compatibility
- archive integrity failure
- untrusted installation
- explicit trust before code loading
- post-trust plugin registration
- upgrade behavior
- dependency-safe removal

Run the canonical suite with:

```bash
python3 -m tests
```

## Deliberate non-goals

Phase 20 does not implement:

- a public remote registry
- automatic code execution
- publisher signing or key management
- automatic trust decisions
- package installation through arbitrary URLs
- a second plugin contract

Those concerns remain outside this first local/package-file distribution boundary.
