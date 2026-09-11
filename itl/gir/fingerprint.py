"""Deterministic fingerprints for generated intermediate representation nodes."""

import json
from dataclasses import fields, is_dataclass
from hashlib import sha256
from typing import Any

from .models import GIRNode


class GIRFingerprint:
    """Create stable SHA-256 fingerprints from GIR node semantics."""

    @classmethod
    def calculate(
        cls,
        node: GIRNode,
    ) -> str:
        """Return the SHA-256 fingerprint for one GIR node."""

        if not isinstance(node, GIRNode):
            raise TypeError(
                "GIR fingerprints can only be calculated "
                "for GIRNode instances."
            )

        canonical = cls.canonicalize(node)
        payload = json.dumps(
            canonical,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

        return sha256(payload).hexdigest()

    @classmethod
    def canonicalize(
        cls,
        value: Any,
    ) -> Any:
        """Convert supported GIR data to an order-independent representation."""

        if isinstance(value, GIRNode):
            return {
                "__type__": type(value).__name__,
                "fields": {
                    field.name: cls.canonicalize(
                        getattr(value, field.name)
                    )
                    for field in fields(value)
                },
            }

        if isinstance(value, dict):
            items = [
                [
                    cls.canonicalize(key),
                    cls.canonicalize(item),
                ]
                for key, item in value.items()
            ]

            return {
                "__type__": "dict",
                "items": cls._sorted(items),
            }

        if isinstance(value, set):
            return {
                "__type__": "set",
                "items": cls._sorted(
                    [cls.canonicalize(item) for item in value]
                ),
            }

        if isinstance(value, list):
            return [cls.canonicalize(item) for item in value]

        if isinstance(value, tuple):
            return {
                "__type__": "tuple",
                "items": [
                    cls.canonicalize(item)
                    for item in value
                ],
            }

        if value is None or isinstance(
            value,
            (bool, int, float, str),
        ):
            return value

        if is_dataclass(value):
            raise TypeError(
                "GIR fingerprints do not support "
                f"non-GIR dataclasses: {type(value).__name__}."
            )

        raise TypeError(
            "GIR fingerprints do not support values "
            f"of type {type(value).__name__}."
        )

    @staticmethod
    def _sorted(values: list[Any]) -> list[Any]:
        return sorted(
            values,
            key=lambda value: json.dumps(
                value,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ),
        )
