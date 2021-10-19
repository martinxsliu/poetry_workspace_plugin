from typing import TYPE_CHECKING, List

from poetry.console.commands.publish import PublishCommand

from poetry_workspace.commands.workspace.workspace import WorkspaceCommand

if TYPE_CHECKING:
    from cleo.io.inputs.option import Option
    from cleo.io.io import IO
    from poetry.poetry import Poetry


def strip_flag_shortcuts(options: List["Option"]) -> List["Option"]:
    for opt in options:
        opt._shortcut = None
    return options


class WorkspacePublishCommand(WorkspaceCommand):
    name = "workspace publish"
    description = "Publishes workspace projects."

    options = strip_flag_shortcuts(PublishCommand.options) + WorkspaceCommand.options

    def handle_each(self, poetry: "Poetry", io: "IO") -> int:
        cmd = PublishCommand()
        cmd.set_poetry(poetry)
        return cmd.execute(io)
