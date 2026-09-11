"""Change classification for incremental GIR builds."""

from dataclasses import dataclass
from enum import Enum


class GIRChangeType(str, Enum):
    ADDED = "ADDED"
    MODIFIED = "MODIFIED"
    UNCHANGED = "UNCHANGED"
    REMOVED = "REMOVED"


@dataclass(frozen=True, slots=True)
class GIRNodeChange:
    node_id: str
    change_type: GIRChangeType
    previous_fingerprint: str | None = None
    current_fingerprint: str | None = None


@dataclass(frozen=True, slots=True)
class GIRChangeSet:
    changes: tuple[GIRNodeChange, ...]

    @property
    def added(self) -> tuple[GIRNodeChange, ...]:
        return self._by_type(GIRChangeType.ADDED)

    @property
    def modified(self) -> tuple[GIRNodeChange, ...]:
        return self._by_type(GIRChangeType.MODIFIED)

    @property
    def unchanged(self) -> tuple[GIRNodeChange, ...]:
        return self._by_type(GIRChangeType.UNCHANGED)

    @property
    def removed(self) -> tuple[GIRNodeChange, ...]:
        return self._by_type(GIRChangeType.REMOVED)

    @property
    def changed(self) -> tuple[GIRNodeChange, ...]:
        return self.added + self.modified + self.removed

    def _by_type(self, change_type: GIRChangeType) -> tuple[GIRNodeChange, ...]:
        return tuple(change for change in self.changes if change.change_type is change_type)


class GIRChangeDetector:
    """Compare persisted and current GIR fingerprints deterministically."""

    @staticmethod
    def detect(
        previous: dict[str, str],
        current: dict[str, str],
    ) -> GIRChangeSet:
        changes = []
        for node_id in sorted(set(previous) | set(current)):
            old = previous.get(node_id)
            new = current.get(node_id)
            if old is None:
                change_type = GIRChangeType.ADDED
            elif new is None:
                change_type = GIRChangeType.REMOVED
            elif old != new:
                change_type = GIRChangeType.MODIFIED
            else:
                change_type = GIRChangeType.UNCHANGED
            changes.append(
                GIRNodeChange(
                    node_id=node_id,
                    change_type=change_type,
                    previous_fingerprint=old,
                    current_fingerprint=new,
                )
            )
        return GIRChangeSet(tuple(changes))
