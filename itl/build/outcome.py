from dataclasses import dataclass

from itl.build.models import BuildPlan
from itl.build.results import BuildResults
from itl.build.summary import BuildSummary


@dataclass(slots=True)
class BuildOutcome:

    plan: BuildPlan

    results: BuildResults

    summary: BuildSummary