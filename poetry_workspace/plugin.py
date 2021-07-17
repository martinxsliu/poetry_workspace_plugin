from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from cleo.events.console_events import COMMAND
from poetry.console.commands.installer_command import EnvCommand, InstallerCommand
from poetry.core.factory import Factory as BaseFactory
from poetry.core.packages.directory_dependency import DirectoryDependency
from poetry.core.pyproject.toml import PyProjectTOML
from poetry.factory import Factory
from poetry.plugins import ApplicationPlugin
from poetry.poetry import Poetry
from poetry.utils.env import EnvManager, SystemEnv, VirtualEnv

if TYPE_CHECKING:
    from cleo.events.console_command_event import ConsoleCommandEvent
    from cleo.events.event_dispatcher import EventDispatcher
    from cleo.io.io import IO
    from poetry.console.application import Application


class WorkspacePlugin(ApplicationPlugin):
    def activate(self, application: "Application") -> None:
        self._workspace_poetry = find_workspace(application)
        if self._workspace_poetry is None:
            return

        configure_poetry_workspace(self._workspace_poetry)

        dispatcher = application.event_dispatcher
        dispatcher.add_listener(COMMAND, self.on_command, priority=1000)

    def on_command(self, event: "ConsoleCommandEvent", _event_name: str, _dispatcher: "EventDispatcher") -> None:
        command = event.command

        if isinstance(command, EnvCommand):
            self.monkeypatch_env_manager()

        if isinstance(command, InstallerCommand):
            self.set_installer_poetry(command, event.io)

    def set_installer_poetry(self, command: InstallerCommand, io: "IO") -> None:
        poetry = Poetry(
            file=BaseFactory.locate(Path.cwd()),
            local_config=self._workspace_poetry.local_config,
            package=self._workspace_poetry.package,
            locker=self._workspace_poetry.locker,
            config=self._workspace_poetry.config,
        )
        Factory().configure_sources(
            poetry,
            poetry.local_config.get("source", []),
            self._workspace_poetry.config,
            io,
        )
        command.set_poetry(poetry)

    def monkeypatch_env_manager(self) -> None:
        workspace_poetry = self._workspace_poetry
        original_method = EnvManager.create_venv

        def create_venv(self, *args, **kwargs) -> Union["SystemEnv", "VirtualEnv"]:
            # Set env manager's Poetry instance to the workspace Poetry instance
            # so that it creates and uses a workspace level virtualenv.
            self._poetry = workspace_poetry
            return original_method(self, *args, **kwargs)

        EnvManager.create_venv = create_venv


def find_workspace(application: "Application") -> Optional[Poetry]:
    try:
        poetry = application.poetry
    except RuntimeError:
        # Could not find a pyproject.toml file in current directory or its parents.
        return

    if is_workspace_pyproject(poetry.pyproject):
        return poetry

    dir_path = poetry.file.path.resolve().parent
    while dir_path != "/":
        if dir_path.parent == dir_path:
            break

        dir_path = dir_path.parent
        pyproject_path = dir_path / "pyproject.toml"
        pyproject = PyProjectTOML(dir_path / "pyproject.toml")
        if is_workspace_pyproject(pyproject):
            return Factory().create_poetry(pyproject_path)


def configure_poetry_workspace(poetry: Poetry) -> None:
    content = poetry.pyproject.data["tool"]["poetry_workspace"]
    if "paths" not in content:
        raise KeyError("Workspace pyproject.toml file requires 'paths' in the 'tool.poetry_workspace' section")

    paths = content["paths"]
    matches = []
    for path in paths:
        pattern = str(poetry.file.path.parent / path / "pyproject.toml")
        matches.extend(glob(pattern, recursive=True))

    requires = set(pkg.name for pkg in poetry.package.requires)

    for match in matches:
        path = Path(match)
        pyproject = PyProjectTOML(path)
        if not pyproject.is_poetry_project():
            continue

        name = pyproject.poetry_config["name"]
        if name in requires:
            continue

        poetry.package.add_dependency(
            DirectoryDependency(
                name=name,
                path=path.parent,
                develop=True,
            )
        )


def is_workspace_pyproject(pyproject: "PyProjectTOML") -> bool:
    return pyproject.file.exists() and bool(pyproject.data.get("tool", {}).get("poetry_workspace"))
