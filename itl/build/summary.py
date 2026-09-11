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
        return self.failed == 0 and self.skipped == 0


def summarize(
    results: BuildResults,
    total_sources: int,
) -> BuildSummary:
    successful = len(results.successful)
    failed = len(results.failed)
    skipped = len(results.skipped)
    processed = successful + failed

    # Account for planned work not represented by an explicit result while
    # preserving the existing summary contract.
    skipped = max(skipped, total_sources - processed)

    return BuildSummary(
        processed=processed,
        successful=successful,
        failed=failed,
        skipped=skipped,
    )
