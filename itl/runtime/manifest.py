from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from itl.gir.models import GIRApplication


class BrowserManifestBuilder:
    """Convert compiler GIR into the stable JSON consumed by the browser runtime."""

    VERSION = "0.1"

    def build(self, applications: Iterable[GIRApplication]) -> dict:
        apps = list(applications)
        if not apps:
            raise ValueError("At least one GIR application is required.")

        first = apps[0]
        pages = []
        seen: set[str] = set()
        for application in apps:
            for page in application.pages:
                if page.name in seen:
                    raise ValueError(f"Duplicate runtime page: {page.name}")
                seen.add(page.name)
                pages.append(asdict(page))

        if not pages:
            raise ValueError("A browser application must contain at least one page.")

        return {
            "version": self.VERSION,
            "application": {
                "name": first.name,
                "target": first.target,
            },
            "initialPage": pages[0]["name"],
            "pages": pages,
        }

    def write(self, applications: Iterable[GIRApplication], path) -> None:
        import json
        from pathlib import Path

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(self.build(applications), indent=2),
            encoding="utf-8",
        )
