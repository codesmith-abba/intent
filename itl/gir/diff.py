"""Deterministic semantic diff analysis for GIR nodes."""

from dataclasses import dataclass, fields
from enum import Enum
from typing import Any

from .fingerprint import GIRFingerprint
from .models import GIRNode


class GIRDiffCategory(str, Enum):
    STYLE = "STYLE"
    LAYOUT = "LAYOUT"
    CONTENT = "CONTENT"
    LOGIC = "LOGIC"
    ARCHITECTURE = "ARCHITECTURE"
    STRUCTURAL = "STRUCTURAL"


@dataclass(frozen=True, slots=True)
class GIRFieldDiff:
    path: str
    previous: Any
    current: Any
    categories: tuple[GIRDiffCategory, ...]


@dataclass(frozen=True, slots=True)
class GIRNodeDiff:
    node_id: str
    categories: tuple[GIRDiffCategory, ...]
    fields: tuple[GIRFieldDiff, ...] = ()
    previous_type: str | None = None
    current_type: str | None = None

    @property
    def changed(self) -> bool:
        return bool(self.categories)


@dataclass(frozen=True, slots=True)
class GIRDiffSet:
    nodes: tuple[GIRNodeDiff, ...]

    @property
    def changed(self) -> tuple[GIRNodeDiff, ...]:
        return tuple(node for node in self.nodes if node.changed)

    @property
    def unchanged(self) -> tuple[GIRNodeDiff, ...]:
        return tuple(node for node in self.nodes if not node.changed)

    def by_category(self, category: GIRDiffCategory) -> tuple[GIRNodeDiff, ...]:
        return tuple(node for node in self.changed if category in node.categories)


class GIRDiffAnalyzer:
    """Compare GIR snapshots and classify semantic changes deterministically."""

    _FIELD_CATEGORIES = {
        "theme": (GIRDiffCategory.STYLE,),
        "colors": (GIRDiffCategory.STYLE,),
        "color": (GIRDiffCategory.STYLE,),
        "typography": (GIRDiffCategory.STYLE,),
        "font": (GIRDiffCategory.STYLE,),
        "spacing": (GIRDiffCategory.STYLE,),
        "padding": (GIRDiffCategory.STYLE,),
        "margin": (GIRDiffCategory.STYLE,),
        "gap": (GIRDiffCategory.STYLE,),
        "background": (GIRDiffCategory.STYLE,),
        "border": (GIRDiffCategory.STYLE,),
        "radius": (GIRDiffCategory.STYLE,),
        "layout": (GIRDiffCategory.LAYOUT,),
        "position": (GIRDiffCategory.LAYOUT,),
        "placement": (GIRDiffCategory.LAYOUT,),
        "order": (GIRDiffCategory.LAYOUT,),
        "alignment": (GIRDiffCategory.LAYOUT,),
        "width": (GIRDiffCategory.LAYOUT,),
        "height": (GIRDiffCategory.LAYOUT,),
        "x": (GIRDiffCategory.LAYOUT,),
        "y": (GIRDiffCategory.LAYOUT,),
        "children": (GIRDiffCategory.LAYOUT, GIRDiffCategory.STRUCTURAL),
        "components": (GIRDiffCategory.LAYOUT, GIRDiffCategory.STRUCTURAL),
        "headline": (GIRDiffCategory.CONTENT,),
        "subtitle": (GIRDiffCategory.CONTENT,),
        "text": (GIRDiffCategory.CONTENT,),
        "label": (GIRDiffCategory.CONTENT,),
        "copy": (GIRDiffCategory.CONTENT,),
        "image": (GIRDiffCategory.CONTENT,),
        "content": (GIRDiffCategory.CONTENT,),
        "action": (GIRDiffCategory.LOGIC,),
        "actions": (GIRDiffCategory.LOGIC,),
        "interaction": (GIRDiffCategory.LOGIC,),
        "interactions": (GIRDiffCategory.LOGIC,),
        "condition": (GIRDiffCategory.LOGIC,),
        "conditions": (GIRDiffCategory.LOGIC,),
        "behavior": (GIRDiffCategory.LOGIC,),
        "logic": (GIRDiffCategory.LOGIC,),
        "handler": (GIRDiffCategory.LOGIC,),
        "event": (GIRDiffCategory.LOGIC,),
        "events": (GIRDiffCategory.LOGIC,),
        "data_flow": (GIRDiffCategory.LOGIC,),
        "frontend": (GIRDiffCategory.ARCHITECTURE,),
        "backend": (GIRDiffCategory.ARCHITECTURE,),
        "api": (GIRDiffCategory.ARCHITECTURE,),
        "database": (GIRDiffCategory.ARCHITECTURE,),
        "cache": (GIRDiffCategory.ARCHITECTURE,),
        "storage": (GIRDiffCategory.ARCHITECTURE,),
        "dependencies": (GIRDiffCategory.ARCHITECTURE, GIRDiffCategory.STRUCTURAL),
        "dependency": (GIRDiffCategory.ARCHITECTURE, GIRDiffCategory.STRUCTURAL),
        "imports": (GIRDiffCategory.ARCHITECTURE, GIRDiffCategory.STRUCTURAL),
    }

    @classmethod
    def analyze(
        cls,
        previous: dict[str, GIRNode],
        current: dict[str, GIRNode],
        previous_dependencies: dict[str, set[str]] | None = None,
        current_dependencies: dict[str, set[str]] | None = None,
    ) -> GIRDiffSet:
        """Analyze two GIR snapshots and optional dependency snapshots."""
        previous_dependencies = previous_dependencies or {}
        current_dependencies = current_dependencies or {}
        nodes = []
        for node_id in sorted(set(previous) | set(current)):
            nodes.append(
                cls._diff_node(
                    node_id,
                    previous.get(node_id),
                    current.get(node_id),
                    previous_dependencies.get(node_id, set()),
                    current_dependencies.get(node_id, set()),
                )
            )
        return GIRDiffSet(tuple(nodes))

    @classmethod
    def _diff_node(
        cls,
        node_id: str,
        previous: GIRNode | None,
        current: GIRNode | None,
        previous_dependencies: set[str],
        current_dependencies: set[str],
    ) -> GIRNodeDiff:
        if previous is None or current is None:
            return GIRNodeDiff(
                node_id=node_id,
                categories=(GIRDiffCategory.STRUCTURAL,),
                previous_type=type(previous).__name__ if previous else None,
                current_type=type(current).__name__ if current else None,
            )

        if type(previous) is not type(current):
            return GIRNodeDiff(
                node_id=node_id,
                categories=(GIRDiffCategory.STRUCTURAL,),
                previous_type=type(previous).__name__,
                current_type=type(current).__name__,
            )

        categories: set[GIRDiffCategory] = set()
        diffs: list[GIRFieldDiff] = []

        previous_fields = {
            field.name: getattr(previous, field.name)
            for field in fields(previous)
        }
        current_fields = {
            field.name: getattr(current, field.name)
            for field in fields(current)
        }

        for field_name in sorted(set(previous_fields) | set(current_fields)):
            old = previous_fields.get(field_name)
            new = current_fields.get(field_name)
            if GIRFingerprint.canonicalize(old) == GIRFingerprint.canonicalize(new):
                continue

            field_categories = cls._categories_for_field(field_name)
            categories.update(field_categories)
            diffs.append(
                GIRFieldDiff(
                    path=field_name,
                    previous=GIRFingerprint.canonicalize(old),
                    current=GIRFingerprint.canonicalize(new),
                    categories=field_categories,
                )
            )

        if previous_dependencies != current_dependencies:
            categories.update(
                {
                    GIRDiffCategory.ARCHITECTURE,
                    GIRDiffCategory.STRUCTURAL,
                }
            )
            diffs.append(
                GIRFieldDiff(
                    path="dependencies",
                    previous=sorted(previous_dependencies),
                    current=sorted(current_dependencies),
                    categories=(
                        GIRDiffCategory.ARCHITECTURE,
                        GIRDiffCategory.STRUCTURAL,
                    ),
                )
            )

        return GIRNodeDiff(
            node_id=node_id,
            categories=tuple(
                category
                for category in GIRDiffCategory
                if category in categories
            ),
            fields=tuple(diffs),
            previous_type=type(previous).__name__,
            current_type=type(current).__name__,
        )

    @classmethod
    def _categories_for_field(
        cls,
        field_name: str,
    ) -> tuple[GIRDiffCategory, ...]:
        return cls._FIELD_CATEGORIES.get(
            field_name.lower(),
            (GIRDiffCategory.STRUCTURAL,),
        )
