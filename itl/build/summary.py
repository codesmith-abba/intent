from dataclasses import dataclass

from itl.build.results import BuildResults


@dataclass(slots=True)
class BuildSummary:

    processed: int

    successful: int

    failed: int

    skipped: int

    @property
    def succeeded(self) -> bool:
        return self.failed == 0


def summarize(
    results: BuildResults,
    total_sources: int,
) -> BuildSummary:

    successful = len(results.successful)
    failed = len(results.failed)

    processed = successful + failed

    skipped = total_sources - processed

    return BuildSummary(
        processed=processed,
        successful=successful,
        failed=failed,
        skipped=skipped,
    )