from poetry_workspace.commands.workspace.changed import WorkspaceChangedCommand
from poetry_workspace.commands.workspace.list import WorkspaceListCommand
from poetry_workspace.commands.workspace.workspace import WorkspaceCommand

WORKSPACE_COMMANDS = [
    WorkspaceChangedCommand,
    WorkspaceListCommand,
]

__all__ = [
    WORKSPACE_COMMANDS,
    WorkspaceCommand,
]
