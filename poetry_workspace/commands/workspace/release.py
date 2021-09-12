from typing import TYPE_CHECKING

from poetry_workspace.commands.release import ReleaseCommand
from poetry_workspace.commands.workspace.workspace import WorkspaceCommand

if TYPE_CHECKING:
    from poetry.poetry import Poetry


class WorkspaceReleaseCommand(WorkspaceCommand):
    name = "workspace release"
    description = "Releases workspace projects."

    options = ReleaseCommand.options + WorkspaceCommand.options

    def handle_each(self, poetry: "Poetry") -> int:
        cmd = ReleaseCommand()
        cmd.set_poetry(poetry)
        return cmd.execute(self.io)
