import json
import tempfile
import unittest
from pathlib import Path

from itl.gir.models import GIRApplication, GIRHero, GIRPage, GIRSection
from itl.gir.writer import IRWriter
from itl.pipeline import Pipeline
from itl.runtime.manifest import BrowserManifestBuilder


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "browser-runtime" / "app.itl"


class BrowserRuntimeManifestTest(unittest.TestCase):
    def test_manifest_uses_gir_and_preserves_pages_components_and_actions(self):
        application = GIRApplication(
            name="Demo",
            target="web",
            intent=None,
            pages=[
                GIRPage(
                    name="home",
                    theme="light",
                    intent="Welcome",
                    components=[
                        GIRHero(
                            name="welcome",
                            intent=None,
                            image="assets/hero.svg",
                            headline="Hello",
                            subtitle="World",
                            action="Go catalog",
                        ),
                        GIRSection(name="featured", intent="Products"),
                    ],
                ),
                GIRPage(name="catalog", theme="light", intent="Catalog"),
            ],
        )

        manifest = BrowserManifestBuilder().build([application])

        self.assertEqual(manifest["version"], "0.1")
        self.assertEqual(manifest["initialPage"], "home")
        self.assertEqual([page["name"] for page in manifest["pages"]], ["home", "catalog"])
        self.assertEqual(manifest["pages"][0]["components"][0]["action"], "Go catalog")

    def test_writer_emits_runtime_manifest_from_real_compiler_gir(self):
        application = Pipeline().compile(EXAMPLE)
        with tempfile.TemporaryDirectory() as directory:
            IRWriter(directory).write(application)
            runtime = json.loads((Path(directory) / "runtime.json").read_text(encoding="utf-8"))

        self.assertEqual(runtime["application"]["target"], "web")
        self.assertEqual(runtime["initialPage"], "home")
        self.assertEqual({page["name"] for page in runtime["pages"]}, {"home", "catalog", "about"})


if __name__ == "__main__":
    unittest.main()
