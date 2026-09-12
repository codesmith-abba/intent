from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile
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
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.build(applications), indent=2) + "\n"
        with NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            delete=False,
        ) as temporary:
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        try:
            os.replace(temporary_path, destination)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise
