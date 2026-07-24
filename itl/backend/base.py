from abc import ABC, abstractmethod
from pathlib import Path


class Backend(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def generate(self, project, output: Path):
        pass