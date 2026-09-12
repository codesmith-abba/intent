from __future__ import annotations

import os
import tempfile
from pathlib import Path
from zipfile import ZipFile

from itl.packages import (
    LocalPackageRegistry,
    PackageBuilder,
    PackageDependency,
    PackageIntegrityError,
    PackageManager,
    PackageManifest,
    PackageReader,
    PackageResolutionError,
    PackageTrustError,
    Version,
    satisfies,
)
from itl.plugins.models import PluginMetadata
from itl.plugins.registry import PluginRegistry


def _plugin_manifest(name: str, version: str, dependencies=()):
    return PackageManifest(
        name=name,
        version=version,
        plugin=PluginMetadata(
            name=name,
            version=version,
            targets=("web",),
            frameworks=("react",),
            capabilities=("generation",),
        ),
        dependencies=tuple(dependencies),
        entry_module=f"{name.replace('-', '_')}_plugin",
    )


def _build_package(root: Path, name: str, version: str, dependencies=(), source=None):
    source_dir = root / f"source-{name}-{version}"
    source_dir.mkdir()
    module_name = f"{name.replace('-', '_')}_plugin.py"
    module_source = source or """
from itl.plugins.models import PluginConfig, PluginMetadata

class DemoPlugin:
    metadata = PluginMetadata(
        name=__name__.split('_plugin')[0].replace('_', '-'),
        version='VERSION',
        targets=('web',),
        frameworks=('react',),
        capabilities=('generation',),
    )

    def configure(self, config: PluginConfig):
        self.config = config

plugin = DemoPlugin()
""".replace("VERSION", version)
    (source_dir / module_name).write_text(module_source)
    manifest = _plugin_manifest(name, version, dependencies)
    output = root / f"{name}-{version}.itlpkg"
    PackageBuilder().build(source_dir, manifest, output)
    return output


def test_version_constraints():
    assert Version.parse("1.2") < Version.parse("1.10")
    assert satisfies("1.5.0", ">=1.0,<2.0")
    assert not satisfies("2.0.0", ">=1.0,<2.0")
    assert satisfies("1.4.0", "^1.2")
    assert satisfies("1.4.0", "~1.4")


def test_local_registry_resolves_highest_compatible_dependency_graph():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _build_package(root, "engine", "1.0.0")
        _build_package(root, "engine", "1.1.0")
        _build_package(
            root,
            "app-plugin",
            "1.0.0",
            dependencies=(PackageDependency("engine", ">=1.0,<2.0"),),
        )

        registry = LocalPackageRegistry(root)
        resolved = registry.resolve("app-plugin")

        assert [item.manifest.name for item in resolved] == ["app-plugin", "engine"]
        engine = next(item for item in resolved if item.manifest.name == "engine")
        assert engine.manifest.version == "1.1.0"


def test_incompatible_plugin_is_not_resolved():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        source = """
from itl.plugins.models import PluginConfig, PluginMetadata
class Demo:
    metadata = PluginMetadata(name='future', version='1.0.0', min_compiler_version='2.0')
    def configure(self, config: PluginConfig):
        pass
plugin = Demo()
"""
        _build_package(root, "future", "1.0.0", source=source)
        registry = LocalPackageRegistry(root)

        try:
            registry.resolve("future", compiler_version="1.0")
        except PackageResolutionError:
            return
        raise AssertionError("Incompatible package was resolved")


def test_package_integrity_rejects_tampered_archive():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        package = _build_package(root, "safe", "1.0.0")
        with ZipFile(package, "a") as archive:
            archive.writestr("unexpected.txt", "tampered")

        try:
            PackageReader().verify(package)
        except PackageIntegrityError:
            return
        raise AssertionError("Tampered package was accepted")


def test_install_is_untrusted_until_explicit_trust_and_load():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        marker = root / "executed.marker"
        os.environ["ITL_TEST_PACKAGE_MARKER"] = str(marker)
        try:
            source = """
import os
from pathlib import Path
from itl.plugins.models import PluginConfig, PluginMetadata
marker = os.environ['ITL_TEST_PACKAGE_MARKER']
Path(marker).write_text('executed')
class Demo:
    metadata = PluginMetadata(name='trusted-demo', version='1.0.0')
    def configure(self, config: PluginConfig):
        self.config = config
plugin = Demo()
"""
            package = _build_package(root, "trusted-demo", "1.0.0", source=source)
            registry = LocalPackageRegistry(root)
            manager = PackageManager(registry, root / "cache")
            installed = manager.install(package)

            assert not installed.trusted
            assert not marker.exists()
            try:
                manager.load_plugin("trusted-demo")
            except PackageTrustError:
                pass
            else:
                raise AssertionError("Untrusted plugin was loaded")
            assert not marker.exists()

            manager.trust("trusted-demo")
            plugin_registry = PluginRegistry()
            plugin = manager.load_plugin("trusted-demo", plugin_registry=plugin_registry)
            assert plugin.metadata.name == "trusted-demo"
            assert marker.exists()
            assert manager.verify("trusted-demo")
        finally:
            os.environ.pop("ITL_TEST_PACKAGE_MARKER", None)


def test_upgrade_and_dependency_safe_removal():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _build_package(root, "engine", "1.0.0")
        _build_package(root, "engine", "1.1.0")
        _build_package(
            root,
            "consumer",
            "1.0.0",
            dependencies=(PackageDependency("engine", "=1.0.0"),),
        )
        registry = LocalPackageRegistry(root)
        manager = PackageManager(registry, root / "cache")
        manager.install(root / "engine-1.0.0.itlpkg")
        manager.install(root / "consumer-1.0.0.itlpkg")

        upgraded = manager.upgrade("engine")
        assert upgraded.version == "1.1.0"
        try:
            manager.remove("engine", "1.1.0")
        except Exception as error:
            assert "consumer" in str(error)
        else:
            raise AssertionError("Dependency was removed while still required")
