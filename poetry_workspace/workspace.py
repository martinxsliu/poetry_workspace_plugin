import os
from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Set

from poetry.core import json
from poetry.core.packages.directory_dependency import DirectoryDependency
from poetry.factory import Factory

from poetry_workspace.errors import WorkspaceError
from poetry_workspace.graph import DependencyGraph

if TYPE_CHECKING:
    from cleo.io.io import IO
    from poetry.core.pyproject.toml import PyProjectTOML
    from poetry.poetry import Poetry


class Workspace:
    _pyproject: "PyProjectTOML"
    _poetry: "Poetry"
    _projects: List["Poetry"]
    _io: "IO"
    _graph: Optional[DependencyGraph]

    def __init__(self, pyproject: "PyProjectTOML", io: "IO"):
        if not is_workspace_pyproject(pyproject):
            raise WorkspaceError("pyproject.toml file does not contain a 'tool.poetry.workspace' section")

        monkeypatch_json_schema()

        self._pyproject = pyproject
        self._poetry = Factory().create_poetry(pyproject.file.path)
        self._io = io
        self._graph = None

        self._projects = self._find_projects(pyproject)
        self._add_project_dependencies()

    @property
    def poetry(self) -> "Poetry":
        return self._poetry

    @property
    def projects(self) -> List["Poetry"]:
        return self._projects

    @property
    def graph(self) -> DependencyGraph:
        if self._graph is None:
            locked_repo = self.poetry.locker.locked_repository(with_dev_reqs=True)
            internal_urls = [str(project.file.path.parent) for project in self.projects]
            self._graph = DependencyGraph(locked_repo, internal_urls)
        return self._graph

    def find_project(self, name: str) -> Optional["Poetry"]:
        for project in self.projects:
            if project.package.name == name:
                return project
        return None

    def _find_projects(self, pyproject: "PyProjectTOML") -> List["Poetry"]:
        content = pyproject.data["tool"]["poetry"]["workspace"]
        if "include" not in content:
            raise WorkspaceError("pyproject.toml file requires 'include' in the 'tool.poetry.workspace' section")

        include = content["include"]
        exclude = content.get("exclude", [])

        matches: Set[str] = set()
        for pattern in include:
            pattern = str(self.poetry.file.path.parent / pattern / "pyproject.toml")
            matches = matches.union(set(glob(pattern, recursive=True)))

        for pattern in exclude:
            pattern = str(self.poetry.file.path.parent / pattern / "pyproject.toml")
            matches = matches.difference(set(glob(pattern, recursive=True)))

        if self._io.is_debug():
            self._io.write_line(f"Using workspace {self.poetry.file.path}")
            self._io.write_line("Found workspace projects:")
            for path in sorted(matches):
                self._io.write_line(f"- {path}")

        return [Factory().create_poetry(Path(path)) for path in sorted(matches)]

    def _add_project_dependencies(self) -> None:
        requires = set(pkg.name for pkg in self.poetry.package.requires)

        for project in self.projects:
            name = project.pyproject.poetry_config["name"]
            if name in requires:
                continue

            self.poetry.package.add_dependency(
                DirectoryDependency(
                    name=name,
                    path=project.file.path.parent,
                    develop=True,
                )
            )


def is_workspace_pyproject(pyproject: "PyProjectTOML") -> bool:
    return pyproject.file.exists() and pyproject.data.get("tool", {}).get("poetry", {}).get("workspace") is not None


def monkeypatch_json_schema() -> None:
    """
    Monkeypatch Poetry's JSON schema for the pyproject.toml file with our custom
    one that includes the schema for `tool.poetry.workspace` section. See
    schemas/gen_schema.py for details.
    """
    json.SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemas")
