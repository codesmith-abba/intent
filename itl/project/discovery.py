from pathlib import Path


class ProjectDiscoverer:

    def discover(
        self,
        start: str | Path,
    ) -> Path:

        current = Path(start).resolve()

        if current.is_file():

            current = current.parent

        while True:

            project_directory = (
                current / ".project"
            )

            if project_directory.is_dir():

                return current

            parent = current.parent

            if parent == current:

                break

            current = parent

        raise FileNotFoundError(
            "Unable to find an ITL project."
        )