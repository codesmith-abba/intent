class PackageError(RuntimeError):
    """Base class for package and registry failures."""


class InvalidPackageError(PackageError):
    """Raised when a package file or manifest is invalid."""


class PackageNotFoundError(PackageError):
    """Raised when a package cannot be found in the local registry."""


class PackageResolutionError(PackageError):
    """Raised when package dependencies cannot be resolved."""


class PackageCompatibilityError(PackageError):
    """Raised when a package is incompatible with the compiler/plugin API."""


class PackageIntegrityError(PackageError):
    """Raised when package contents fail integrity verification."""


class PackageInstalledError(PackageError):
    """Raised when an installation conflicts with installed state."""


class PackageTrustError(PackageError):
    """Raised when executable plugin code has not been explicitly trusted."""
