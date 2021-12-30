from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

from cleo.events.console_events import COMMAND
from poetry.console.commands.installer_command import EnvCommand, InstallerCommand
from poetry.core.factory import Factory as BaseFactory
from poetry.core.pyproject.toml import PyProjectTOML
from poetry.core.version.pep440.version import PEP440Version
from poetry.factory import Factory
from poetry.plugins import ApplicationPlugin
from poetry.poetry import Poetry

from poetry_workspace.commands import loader
from poetry_workspace.commands.workspace.workspace import WorkspaceCommand
from poetry_workspace.workspace import Workspace, is_workspace_pyproject

if TYPE_CHECKING:
    from cleo.events.console_command_event import ConsoleCommandEvent
    from cleo.events.event_dispatcher import EventDispatcher
    from cleo.io.io import IO
    from poetry.console.application import Application


class WorkspacePlugin(ApplicationPlugin):
    def activate(self, application: "Application") -> None:
        loader.register_commands(application.command_loader)

        dispatcher = application.event_dispatcher
        dispatcher.add_listener(COMMAND, self.on_command, priority=1000)

    def on_command(self, event: "ConsoleCommandEvent", _event_name: str, _dispatcher: "EventDispatcher") -> None:
        command = event.command

        monkeypatch_version_parser()

        workspace = find_workspace(command.application, event.io)
        if workspace is None:
            return

        if isinstance(command, EnvCommand):
            monkeypatch_env_manager(workspace)

        if isinstance(command, InstallerCommand):
            set_installer_poetry(command, event.io, workspace)
            monkeypatch_version_solver(workspace)

        if isinstance(command, WorkspaceCommand):
            command.set_workspace(workspace)


def set_installer_poetry(command: InstallerCommand, io: "IO", workspace: Workspace) -> None:
    poetry = Poetry(
        file=BaseFactory.locate(Path.cwd()),
        local_config=workspace.poetry.local_config,
        package=workspace.poetry.package,
        locker=workspace.poetry.locker,
        config=workspace.poetry.config,
    )
    Factory().configure_sources(
        poetry,
        poetry.local_config.get("source", []),
        workspace.poetry.config,
        io,
    )
    command.set_poetry(poetry)


def monkeypatch_env_manager(workspace: Workspace) -> None:
    from poetry.utils.env import EnvManager, SystemEnv, VirtualEnv

    workspace_poetry = workspace.poetry
    original_method = EnvManager.create_venv

    def create_venv(self: EnvManager, *args: Any, **kwargs: Any) -> Union[SystemEnv, VirtualEnv]:
        # Set env manager's Poetry instance to the workspace Poetry instance
        # so that it creates and uses a workspace level virtualenv.
        self._poetry = workspace_poetry
        return original_method(self, *args, **kwargs)

    EnvManager.create_venv = create_venv


def monkeypatch_version_solver(workspace: Workspace) -> None:
    """
    Normally if a workspace project's dependencies are changed, then the workspace
    will resolve the changed dependencies if an update operation was performed for
    the workspace project (e.g. `poetry lock`, `poetry update`, or `poetry update
    foo`). If an update operation was not performed (e.g. `poetry lock --no-update`,
    or `poetry update not-foo`) then the changed dependencies will not be resolved.

    We want to resolve workspace project dependencies all the time as if they are
    direct dependencies of the workspace root project, regardless of whether an
    update was performed or not. This method monkey patches the `VersionSolver` class
    so that all workspace projects are included in the `use_latest` list to ensure
    that the resolver always uses the latest version of workspace projects.
    """
    from poetry.mixology.result import SolverResult
    from poetry.mixology.version_solver import VersionSolver

    original_method = VersionSolver.solve
    workspace_packages = set(project.package.name for project in workspace.projects)

    def solve(self: VersionSolver) -> SolverResult:
        self._use_latest = sorted(set(self._use_latest) | workspace_packages)
        return original_method(self)

    VersionSolver.solve = solve


def monkeypatch_version_parser() -> None:
    """
    Workaround for https://github.com/python-poetry/poetry/issues/4176.
    """
    original_method = PEP440Version.parse

    def parse(cls, value: str):
        if value:
            value = value.rstrip(".")
        return original_method.__func__(cls, value)

    PEP440Version.parse = classmethod(parse)


def find_workspace(application: "Application", io: "IO") -> Optional[Workspace]:
    cwd = Path.cwd()
    for dir_path in [cwd] + list(cwd.parents):
        pyproject = PyProjectTOML(dir_path / "pyproject.toml")
        if not is_workspace_pyproject(pyproject):
            continue

        workspace = Workspace(pyproject, io)
        if workspace.poetry.file.path == application.poetry.file.path:
            # Currently in workspace's root project tree.
            return workspace

        for project in workspace.projects:
            if project.file.path == application.poetry.file.path:
                # Currently in a workspace project's tree.
                return workspace

    return None
