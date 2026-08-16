class ProjectError(Exception):
    """Base exception for project errors."""


class ProjectStateError(ProjectError):
    """Invalid or unreadable project state."""