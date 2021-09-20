from importlib import import_module
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from poetry.console.command_loader import CommandLoader
    from poetry.console.commands.command import Command

COMMAND_NAMES = [
    "build",
    "workspace build",
    "workspace list",
    "workspace publish",
    "workspace run",
    "workspace version",
]


def register_commands(command_loader: "CommandLoader") -> None:
    def load_plugin_command(name: str) -> Callable[[], "Command"]:
        def _load() -> "Command":
            module = import_module("poetry_workspace.commands.{}".format(".".join(name.split(" "))))
            command_class = getattr(module, "{}Command".format("".join(c.title() for c in name.split(" "))))
            return command_class()

        return _load

    for name in COMMAND_NAMES:
        # Set _factories directly instead of calling the register_factory method
        # because we want to override Poetry's base commands.
        command_loader._factories[name] = load_plugin_command(name)
