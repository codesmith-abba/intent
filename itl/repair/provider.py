from dataclasses import dataclass, field
from typing import Any, Protocol

from itl.repair.models import RepairRequest


@dataclass(frozen=True, slots=True)
class RepairProviderResponse:
    output: str
    provider: str
    model: str
    metadata: dict[str, Any] = field(default_factory=dict)


class RepairProvider(Protocol):
    """Provider boundary for repairing one generated build unit."""

    def repair(
        self,
        request: RepairRequest,
        prompt: str,
    ) -> RepairProviderResponse:
        ...
