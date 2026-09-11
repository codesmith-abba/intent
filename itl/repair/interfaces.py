from typing import Protocol

from itl.build.models import BuildItem
from itl.repair.models import RepairResult
from itl.validation.models import ValidationReport


class Repairer(Protocol):
    """Build-executor boundary for repairing one failed build unit."""

    def repair(
        self,
        item: BuildItem,
        output: str,
        report: ValidationReport,
    ) -> RepairResult:
        ...
