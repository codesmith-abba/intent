from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from itl.build.executor import BuildExecutor
from itl.build.pipeline import BuildPipeline
from itl.build.planner import BuildPlanner
from itl.cache.cache import Cache
from itl.cache.decider import CacheDecider
from itl.emit.emitter import Emitter
from itl.generation.generator import AIGenerator
from itl.generation.models import GenerationContext, GenerationRequest
from itl.gir.diff import GIRDiffAnalyzer, GIRDiffCategory
from itl.gir.fingerprint import GIRFingerprint
from itl.gir.store import GIRFingerprintStore
from itl.graph.graph import DependencyGraph
from itl.pipeline import Pipeline
from itl.plugins.reference_react import ReactReferencePlugin
from itl.plugins.registry import PluginManager, PluginRegistry
from itl.repair.models import RepairPolicy
from itl.repair.provider import RepairProviderResponse
from itl.repair.repairer import AIRepairer
from itl.validation.models import ValidationContext
from itl.validation.pipeline import ValidatorPipeline
from itl.validation.plugin import PluginValidator


EXAMPLE_DIR = Path(__file__).parents[1] / "examples" / "storefront"
UNIT_NAMES = ("shell", "home", "catalog", "product", "checkout")


class ReferenceRepairProvider:
    def repair(self, request, prompt):
        return RepairProviderResponse(
            output=(
                "export default function RepairedComponent() {\n"
                "  return <div>Repaired storefront component</div>;\n"
                "}\n"
            ),
            provider="phase16-repair",
            model="reference-repair",
        )


class Phase16E2ETest(unittest.TestCase):
    def copy_example(self, root: Path) -> list[Path]:
        paths = []
        for name in UNIT_NAMES:
            source = EXAMPLE_DIR / f"{name}.itl"
            target = root / f"{name}.itl"
            shutil.copy2(source, target)
            paths.append(target)
        return paths

    def compile_units(self, sources: list[Path]):
        compiler = Pipeline()
        return {
            str(source): compiler.compile(source).pages[0]
            for source in sources
        }

    def diff_nodes(self, pages):
        nodes = dict(pages)
        for source, page in pages.items():
            for component in page.components:
                component_id = f"{source}#{component.name}"
                nodes[component_id] = component
        return nodes

    def make_graph(self, sources: list[Path]) -> DependencyGraph:
        by_name = {source.stem: str(source) for source in sources}
        graph = DependencyGraph()
        for source in sources:
            graph.add_node(str(source))

        graph.add_dependency(by_name["home"], by_name["shell"])
        graph.add_dependency(by_name["catalog"], by_name["home"])
        graph.add_dependency(by_name["product"], by_name["catalog"])
        graph.add_dependency(by_name["checkout"], by_name["product"])
        return graph

    def make_pipeline(self, root: Path, sources: list[Path], graph: DependencyGraph):
        cache = Cache(root / ".project" / "cache")
        registry = PluginRegistry()
        registry.register(ReactReferencePlugin())
        manager = PluginManager(registry)

        gir = self.compile_units(sources)
        contexts = {
            source: GenerationContext(
                unit_id=source,
                unit_type=type(node).__name__,
                intent=node.intent,
                dependencies=tuple(sorted(graph.dependencies_of(source))),
                target="web",
                framework="react",
            )
            for source, node in gir.items()
        }

        generator = AIGenerator(
            manager.generation_provider(),
            contexts,
            cache=cache,
        )

        validator = ValidatorPipeline(
            [
                PluginValidator(
                    manager,
                    lambda context: GenerationRequest(
                        context=contexts[context.unit_id],
                        requested_unit=context.unit_id,
                    ),
                )
            ]
        )

        executor = BuildExecutor(
            generator.build,
            validator=validator,
            validation_context_factory=lambda item, output: ValidationContext(
                unit_id=item.source,
                source=item.source,
                output=output,
            ),
        )

        fingerprints = {
            source: GIRFingerprint.calculate(node)
            for source, node in gir.items()
        }

        pipeline = BuildPipeline(
            BuildPlanner(CacheDecider(cache), graph),
            executor,
            gir_store=GIRFingerprintStore(root / ".project" / "gir" / "fingerprints.json"),
            emitter=Emitter(root / "output"),
        )
        return pipeline, fingerprints, gir, contexts

    def refresh_contexts(self, contexts, gir, graph):
        for source, node in gir.items():
            contexts[source] = GenerationContext(
                unit_id=source,
                unit_type=type(node).__name__,
                intent=node.intent,
                dependencies=tuple(sorted(graph.dependencies_of(source))),
                target="web",
                framework="react",
            )

    def test_real_application_incremental_workflow(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            example_root = root / "storefront"
            example_root.mkdir()
            sources = self.copy_example(example_root)
            graph = self.make_graph(sources)

            pipeline, fingerprints, previous_gir, contexts = self.make_pipeline(root, sources, graph)
            previous_nodes = self.diff_nodes(previous_gir)

            initial = pipeline.build(sources, gir_fingerprints=fingerprints)
            self.assertTrue(initial.results.succeeded)
            self.assertEqual(initial.summary.successful, 5)
            self.assertIsNotNone(initial.emission)
            self.assertEqual(len(initial.emission.created), 5)
            for source in sources:
                self.assertTrue((root / "output" / f"{source.stem}.generated").exists())

            unchanged = pipeline.build(sources, gir_fingerprints=fingerprints)
            self.assertTrue(unchanged.summary.succeeded)
            self.assertEqual(unchanged.summary.processed, 0)
            self.assertEqual(unchanged.summary.skipped, 5)

            home = next(source for source in sources if source.stem == "home")
            home_text = home.read_text(encoding="utf-8")
            home.write_text(
                home_text.replace(
                    "Discover products made for everyday life",
                    "Discover products for everyday life",
                ),
                encoding="utf-8",
            )
            changed_gir = self.compile_units(sources)
            self.refresh_contexts(contexts, changed_gir, graph)
            changed_fingerprints = {
                source: GIRFingerprint.calculate(node) for source, node in changed_gir.items()
            }
            content_diff = GIRDiffAnalyzer.analyze(previous_nodes, self.diff_nodes(changed_gir))
            home_hero_id = f"{home}#welcome"
            self.assertIn(
                GIRDiffCategory.CONTENT,
                next(node.categories for node in content_diff.changed if node.node_id == home_hero_id),
            )
            content_build = pipeline.build(sources, gir_fingerprints=changed_fingerprints)
            self.assertEqual(content_build.summary.successful, 4)
            self.assertEqual(content_build.summary.processed, 4)
            previous_gir = changed_gir
            previous_nodes = self.diff_nodes(changed_gir)
            fingerprints = changed_fingerprints

            catalog = next(source for source in sources if source.stem == "catalog")
            catalog_text = catalog.read_text(encoding="utf-8")
            catalog.write_text(catalog_text.replace("theme $light", "theme $dark"), encoding="utf-8")
            styled_gir = self.compile_units(sources)
            self.refresh_contexts(contexts, styled_gir, graph)
            styled_fingerprints = {
                source: GIRFingerprint.calculate(node) for source, node in styled_gir.items()
            }
            style_diff = GIRDiffAnalyzer.analyze(previous_nodes, self.diff_nodes(styled_gir))
            catalog_diff = next(node for node in style_diff.changed if node.node_id == str(catalog))
            self.assertIn(GIRDiffCategory.STYLE, catalog_diff.categories)
            style_build = pipeline.build(sources, gir_fingerprints=styled_fingerprints)
            self.assertEqual(style_build.summary.successful, 3)
            self.assertEqual(style_build.summary.processed, 3)
            previous_gir = styled_gir
            previous_nodes = self.diff_nodes(styled_gir)
            fingerprints = styled_fingerprints

            product = next(source for source in sources if source.stem == "product")
            product_text = product.read_text(encoding="utf-8")
            product.write_text(
                product_text.replace(
                    "section $delivery",
                    "section $reviews {\n            intent $(\n\n                Show recent customer feedback.\n\n            )\n\n            headline $Customer reviews\n        }\n\n        section $delivery",
                ),
                encoding="utf-8",
            )
            structural_gir = self.compile_units(sources)
            self.refresh_contexts(contexts, structural_gir, graph)
            structural_fingerprints = {
                source: GIRFingerprint.calculate(node) for source, node in structural_gir.items()
            }
            structural_diff = GIRDiffAnalyzer.analyze(previous_nodes, self.diff_nodes(structural_gir))
            product_diff = next(node for node in structural_diff.changed if node.node_id == str(product))
            self.assertIn(GIRDiffCategory.STRUCTURAL, product_diff.categories)
            structural_build = pipeline.build(sources, gir_fingerprints=structural_fingerprints)
            self.assertEqual(structural_build.summary.successful, 2)
            self.assertEqual(structural_build.summary.processed, 2)
            previous_gir = structural_gir
            previous_nodes = self.diff_nodes(structural_gir)
            fingerprints = structural_fingerprints

            checkout = next(source for source in sources if source.stem == "checkout")
            checkout_text = checkout.read_text(encoding="utf-8")
            checkout.write_text(
                checkout_text.replace("Complete your order", "Complete your secure order"),
                encoding="utf-8",
            )
            new_graph = self.make_graph(sources)
            shell = next(source for source in sources if source.stem == "shell")
            new_graph.add_dependency(str(checkout), str(shell))
            dependency_gir = self.compile_units(sources)
            self.refresh_contexts(contexts, dependency_gir, new_graph)
            dependency_fingerprints = {
                source: GIRFingerprint.calculate(node) for source, node in dependency_gir.items()
            }
            dependency_diff = GIRDiffAnalyzer.analyze(
                previous_nodes,
                self.diff_nodes(dependency_gir),
                {str(checkout): graph.dependencies_of(str(checkout))},
                {str(checkout): new_graph.dependencies_of(str(checkout))},
            )
            checkout_diff = next(node for node in dependency_diff.changed if node.node_id == str(checkout))
            self.assertIn(GIRDiffCategory.ARCHITECTURE, checkout_diff.categories)
            self.assertIn(GIRDiffCategory.STRUCTURAL, checkout_diff.categories)

            pipeline, _, _, _ = self.make_pipeline(root, sources, new_graph)
            dependency_build = pipeline.build(sources, gir_fingerprints=dependency_fingerprints)
            self.assertTrue(dependency_build.results.succeeded)
            self.assertGreaterEqual(dependency_build.summary.processed, 1)
            self.assertTrue((root / "output" / "checkout.generated").exists())

    def test_validation_failure_repair_and_emission(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            example_root = root / "storefront"
            example_root.mkdir()
            sources = self.copy_example(example_root)
            source = next(path for path in sources if path.stem == "product")
            graph = self.make_graph(sources)
            gir = self.compile_units(sources)
            source_id = str(source)
            context = GenerationContext(
                unit_id=source_id,
                unit_type=type(gir[source_id]).__name__,
                intent=gir[source_id].intent,
                target="web",
                framework="react",
                dependencies=tuple(sorted(graph.dependencies_of(source_id))),
            )
            contexts = {source_id: context}

            registry = PluginRegistry()
            registry.register(ReactReferencePlugin())
            manager = PluginManager(registry)
            validator = ValidatorPipeline(
                [
                    PluginValidator(
                        manager,
                        lambda validation_context: GenerationRequest(
                            context=contexts[validation_context.unit_id],
                            requested_unit=validation_context.unit_id,
                        ),
                    )
                ]
            )

            def invalid_builder(item):
                return "<broken-output />"

            repairer = AIRepairer(
                ReferenceRepairProvider(),
                contexts,
                validator,
                policy=RepairPolicy(max_attempts=1),
                validation_context_factory=lambda item, output: ValidationContext(
                    unit_id=item.source,
                    source=item.source,
                    output=output,
                ),
            )

            cache = Cache(root / ".project" / "cache")
            pipeline = BuildPipeline(
                BuildPlanner(CacheDecider(cache), graph),
                BuildExecutor(
                    invalid_builder,
                    validator=validator,
                    validation_context_factory=lambda item, output: ValidationContext(
                        unit_id=item.source,
                        source=item.source,
                        output=output,
                    ),
                    repairer=repairer,
                ),
                emitter=Emitter(root / "output"),
            )

            outcome = pipeline.build([source])
            self.assertTrue(outcome.results.succeeded)
            result = outcome.results.successful[0]
            self.assertIsNotNone(result.validation_report)
            self.assertTrue(result.validation_report.passed)
            self.assertIn("Repaired storefront component", result.output)

            self.assertIsNotNone(outcome.emission)
            self.assertEqual(len(outcome.emission.created), 1)
            emitted = root / "output" / "product.generated"
            self.assertTrue(emitted.exists())
            self.assertIn("Repaired storefront component", emitted.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
