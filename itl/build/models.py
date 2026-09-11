from dataclasses import dataclass, field

from itl.cache.decision import CacheStatus


@dataclass(slots=True)
class BuildItem:

    source: str

    status: CacheStatus

    dependencies: set[str] = field(
        default_factory=set
    )


@dataclass(slots=True)
class BuildPlan:

    items: list[BuildItem] = field(
        default_factory=list
    )

    removed: list[str] = field(
        default_factory=list
    )

    def add(
        self,
        item: BuildItem,
    ):

        self.items.append(item)

    @property
    def sources(self) -> list[str]:

        return [
            item.source
            for item in self.items
        ]

    def ordered(
        self,
        order: list[str],
    ) -> "BuildPlan":

        items = {
            item.source: item
            for item in self.items
        }

        return BuildPlan(
            items=[
                items[source]
                for source in order
                if source in items
            ],
            removed=list(self.removed),
        )
