from typing import TYPE_CHECKING

from poetry.console.commands.version import VersionCommand

from poetry_workspace.commands.workspace.workspace import WorkspaceCommand

if TYPE_CHECKING:
    from cleo.io.io import IO
    from poetry.poetry import Poetry


class WorkspaceVersionCommand(WorkspaceCommand):
    name = "workspace version"
    description = "Shows or bumps the versions of workspace projects."

    arguments = VersionCommand.arguments
    options = VersionCommand.options + WorkspaceCommand.options

    def handle_each(self, poetry: "Poetry", io: "IO") -> int:
        cmd = VersionCommand()
        cmd.set_poetry(poetry)
        return cmd.execute(io)
