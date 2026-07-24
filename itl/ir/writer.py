import json
from dataclasses import asdict
from pathlib import Path


class IRWriter:

    def write(self, project):

        root = Path(".project")

        root.mkdir(exist_ok=True)

        (root / "assets").mkdir(exist_ok=True)
        (root / "cache").mkdir(exist_ok=True)
        (root / "logs").mkdir(exist_ok=True)

        with open(root / "app.json", "w") as f:
            json.dump(asdict(project), f, indent=4)

        metadata = {
            "version": "0.1.0",
            "framework": project.framework,
            "target": project.target
        }

        with open(root / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)

        graph = {
            "pages": [
                page.name
                for page in project.pages
            ]
        }

        with open(root / "graph.json", "w") as f:
            json.dump(graph, f, indent=4)