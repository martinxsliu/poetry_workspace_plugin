from glob import glob
from typing import TYPE_CHECKING, List

from poetry.core.packages.directory_dependency import DirectoryDependency
from poetry.factory import Factory

if TYPE_CHECKING:
    from cleo.io.io import IO
    from poetry.core.pyproject.toml import PyProjectTOML
    from poetry.poetry import Poetry


class Workspace:
    _pyproject: "PyProjectTOML"
    _poetry: "Poetry"
    _projects: List["Poetry"]
    _io: "IO"

    def __init__(self, pyproject: "PyProjectTOML", io: "IO"):
        self._pyproject = pyproject
        self._poetry = Factory().create_poetry(pyproject.file.path)
        self._io = io

        self._projects = self._find_projects(pyproject)
        self._add_project_dependencies()

    @property
    def poetry(self) -> "Poetry":
        return self._poetry

    @property
    def projects(self) -> List["Poetry"]:
        return self._projects

    def _find_projects(self, pyproject: "PyProjectTOML") -> List["Poetry"]:
        content = pyproject.data["tool"]["poetry_workspace"]
        if "include" not in content:
            raise KeyError("Workspace pyproject.toml file requires 'include' in the 'tool.poetry_workspace' section")

        include = content["include"]
        exclude = content.get("exclude", [])

        matches = set()
        for pattern in include:
            pattern = str(self.poetry.file.path.parent / pattern / "pyproject.toml")
            matches = matches.union(set(glob(pattern, recursive=True)))

        for pattern in exclude:
            pattern = str(self.poetry.file.path.parent / pattern / "pyproject.toml")
            matches = matches.difference(set(glob(pattern, recursive=True)))

        if self._io.is_very_verbose():
            self._io.write_line(f"Using workspace {self.poetry.file.path}")
            self._io.write_line("Found workspace projects:")
            for path in sorted(matches):
                self._io.write_line(f"- {path}")

        return [Factory().create_poetry(path) for path in sorted(matches)]

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
