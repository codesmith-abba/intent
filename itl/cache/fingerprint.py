from hashlib import sha256
from pathlib import Path


class SourceFingerprint:

    @staticmethod
    def calculate(path: str | Path) -> str:

        path = Path(path)

        content = path.read_bytes()

        return sha256(content).hexdigest()