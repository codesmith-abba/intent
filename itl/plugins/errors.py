class PluginError(RuntimeError):
    """Base class for plugin system failures."""


class InvalidPluginError(PluginError):
    """Raised when a plugin does not satisfy the base contract."""


class DuplicatePluginError(PluginError):
    """Raised when two plugins register the same plugin name."""


class IncompatiblePluginError(PluginError):
    """Raised when a plugin cannot run with the current compiler/API."""


class PluginNotFoundError(PluginError):
    """Raised when no registered plugin matches a requested target/framework."""


class PluginSelectionError(PluginError):
    """Raised when plugin selection is ambiguous."""


class PluginCapabilityError(PluginError):
    """Raised when a selected plugin lacks a requested capability."""
