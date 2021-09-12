from typing import TYPE_CHECKING

from poetry.console.commands.build import BuildCommand
from poetry.console.commands.env_command import EnvCommand

from poetry_workspace.commands.workspace.workspace import WorkspaceCommand

if TYPE_CHECKING:
    from poetry.poetry import Poetry


class WorkspaceBuildCommand(WorkspaceCommand, EnvCommand):
    name = "workspace build"
    description = "Builds workspace projects."

    options = BuildCommand.options + WorkspaceCommand.options
    loggers = BuildCommand.loggers

    def handle_each(self, poetry: "Poetry") -> int:
        cmd = BuildCommand()
        cmd.set_env(self.env)
        cmd.set_poetry(poetry)
        return cmd.execute(self.io)
