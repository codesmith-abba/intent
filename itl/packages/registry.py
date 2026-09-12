from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path

from itl.plugins.models import PLUGIN_API_VERSION

from .errors import PackageCompatibilityError, PackageNotFoundError, PackageResolutionError
from .format import PackageReader
from .models import PackageManifest, ResolvedPackage


@total_ordering
@dataclass(frozen=True, slots=True)
class Version:
    parts: tuple[int, ...]

    @classmethod
    def parse(cls, value: str) -> "Version":
        try:
            parts = tuple(int(part) for part in value.split("."))
        except ValueError as error:
            raise ValueError(f"Invalid version '{value}'.") from error
        if not parts or any(part < 0 for part in parts):
            raise ValueError(f"Invalid version '{value}'.")
        return cls(parts)

    def _normalized(self) -> tuple[int, int, int]:
        values = self.parts + (0, 0, 0)
        return values[:3]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._normalized() == other._normalized()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._normalized() < other._normalized()

    def __str__(self) -> str:
        return ".".join(str(part) for part in self.parts)


def satisfies(version: str, constraint: str) -> bool:
    current = Version.parse(version)
    constraint = constraint.strip()
    if constraint in ("", "*"):
        return True
    for expression in constraint.split(","):
        expression = expression.strip()
        if not expression:
            continue
        if expression.startswith(">="):
            if current < Version.parse(expression[2:]):
                return False
        elif expression.startswith("<="):
            if current > Version.parse(expression[2:]):
                return False
        elif expression.startswith(">"):
            if not current > Version.parse(expression[1:]):
                return False
        elif expression.startswith("<"):
            if not current < Version.parse(expression[1:]):
                return False
        elif expression.startswith("^"):
            base = Version.parse(expression[1:])
            if current < base or current >= Version((base.parts[0] + 1,)):
                return False
        elif expression.startswith("~"):
            base = Version.parse(expression[1:])
            upper = Version((base.parts[0], base.parts[1] + 1 if len(base.parts) > 1 else 1))
            if current < base or current >= upper:
                return False
        elif current != Version.parse(expression):
            return False
    return True


@dataclass(frozen=True, slots=True)
class _Candidate:
    manifest: PackageManifest
    source: Path


class LocalPackageRegistry:
    """File-backed package registry; it never imports or executes package code."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.reader = PackageReader()
        self._cache: dict[Path, _Candidate] = {}

    def packages(self, name: str | None = None) -> tuple[ResolvedPackage, ...]:
        candidates = []
        if not self.root.exists():
            return ()
        for path in sorted(self.root.glob("*.itlpkg")):
            try:
                manifest = self._load(path).manifest
            except Exception:
                continue
            if name is None or manifest.name.casefold() == name.casefold():
                candidates.append(ResolvedPackage(manifest, str(path)))
        candidates.sort(key=lambda item: Version.parse(item.manifest.version), reverse=True)
        return tuple(candidates)

    def candidates(self, name: str) -> tuple[ResolvedPackage, ...]:
        return self.packages(name)

    def resolve(
        self,
        name: str,
        constraint: str = "*",
        compiler_version: str = "1.0",
    ) -> tuple[ResolvedPackage, ...]:
        resolver = PackageResolver(self, compiler_version=compiler_version)
        return resolver.resolve(name, constraint)

    def _load(self, path: Path) -> _Candidate:
        cached = self._cache.get(path)
        if cached is not None:
            return cached
        manifest = self.reader.verify(path)
        candidate = _Candidate(manifest, path)
        self._cache[path] = candidate
        return candidate


class PackageResolver:
    """Deterministic dependency resolver with backtracking and compatibility checks."""

    def __init__(self, registry: LocalPackageRegistry, compiler_version: str = "1.0"):
        self.registry = registry
        self.compiler_version = compiler_version

    def resolve(self, name: str, constraint: str = "*") -> tuple[ResolvedPackage, ...]:
        result = self._search({name.casefold(): constraint}, {})
        if result is None:
            raise PackageResolutionError(
                f"Unable to resolve package '{name}' with constraint '{constraint}'."
            )
        return tuple(result[key] for key in sorted(result))

    def _search(
        self,
        constraints: dict[str, str],
        selected: dict[str, ResolvedPackage],
    ) -> dict[str, ResolvedPackage] | None:
        unresolved = [key for key in constraints if key not in selected]
        if not unresolved:
            for key, package in selected.items():
                if not satisfies(package.manifest.version, constraints[key]):
                    return None
            return selected

        key = sorted(unresolved)[0]
        candidates = [
            package
            for package in self.registry.candidates(key)
            if satisfies(package.manifest.version, constraints[key])
            and self._compatible(package.manifest)
        ]
        if not candidates:
            return None

        for package in candidates:
            next_selected = dict(selected)
            next_selected[key] = package
            next_constraints = dict(constraints)
            valid = True
            for dependency in package.manifest.dependencies:
                dep_key = dependency.name.casefold()
                previous = next_constraints.get(dep_key)
                if previous is None:
                    next_constraints[dep_key] = dependency.constraint
                elif not _constraints_compatible(previous, dependency.constraint):
                    valid = False
                    break
                else:
                    next_constraints[dep_key] = f"{previous},{dependency.constraint}"
                chosen = next_selected.get(dep_key)
                if chosen is not None and not satisfies(chosen.manifest.version, next_constraints[dep_key]):
                    valid = False
                    break
            if not valid:
                continue
            result = self._search(next_constraints, next_selected)
            if result is not None:
                return result
        return None

    def _compatible(self, manifest: PackageManifest) -> bool:
        if manifest.plugin is None:
            return True
        if manifest.plugin.api_version != PLUGIN_API_VERSION:
            return False
        from .registry import satisfies as _satisfies
        return _compiler_in_range(
            self.compiler_version,
            manifest.plugin.min_compiler_version,
            manifest.plugin.max_compiler_version,
        )


def _compiler_in_range(current: str, minimum: str, maximum: str | None) -> bool:
    if Version.parse(current) < Version.parse(minimum):
        return False
    if maximum is not None and Version.parse(current) > Version.parse(maximum):
        return False
    return True


def _constraints_compatible(first: str, second: str) -> bool:
    probes = ["0.0.0", "1.0.0", "2.0.0", "10.0.0"]
    return any(satisfies(probe, first) and satisfies(probe, second) for probe in probes)
