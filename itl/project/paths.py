from pathlib import Path


class ProjectPaths:

    def __init__(
        self,
        root: str | Path,
    ):

        self.root = Path(root)

    @property
    def project(self) -> Path:

        return self.root / ".project"

    @property
    def state(self) -> Path:

        return self.project / "state.json"

    @property
    def cache(self) -> Path:

        return self.project / "cache"

    @property
    def graph(self) -> Path:

        return self.project / "graph"

    @property
    def gir(self) -> Path:

        return self.project / "gir"

    @property
    def generation(self) -> Path:

        return self.project / "generation"
    
    @property
    def gitignore(self) -> Path:

        return self.project / ".gitignore"