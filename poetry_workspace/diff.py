import tempfile
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from poetry.factory import Factory

from poetry_workspace.graph import DependencyGraph
from poetry_workspace.vcs import VCS, detect_vcs
from poetry_workspace.workspace import Workspace

if TYPE_CHECKING:
    from cleo.io.io import IO
    from poetry.core.packages.package import Package
    from poetry.poetry import Poetry


class Diff:
    _workspace: Workspace
    _graph: DependencyGraph
    _vcs: VCS
    _io: "IO"

    def __init__(self, workspace: Workspace, graph: DependencyGraph, vcs: VCS = None, io: "IO" = None):
        self._workspace = workspace
        self._graph = graph
        self._vcs = vcs or detect_vcs()

        if io is None:
            from cleo.io.null_io import NullIO

            io = NullIO()
        self._io = io

    def get_changed_projects(self, ref: str) -> List["Package"]:
        package_paths = [(package, Path(package.source_url)) for package in self._graph.search()]

        def find_parent_project(file: Path) -> Optional["Package"]:
            for package, package_path in package_paths:
                try:
                    file.relative_to(package_path)
                    return package
                except ValueError:
                    pass
            return None

        changed_files = self.get_changed_files(ref)
        changed_projects = defaultdict(list)
        other_files = []

        for file in changed_files:
            package = find_parent_project(file)
            if package:
                changed_projects[package].append(file)
            else:
                other_files.append(file)

        if self._io.is_very_verbose():
            for package, files in changed_projects.items():
                self._io.write_line(f"Detected changes in project <info>{package.source_url}</info>:")
                for file in sorted(files):
                    self._io.write_line(f"- {file}")

            if other_files:
                self._io.write_line("Changed files not belonging to any project:")
                for file in sorted(other_files):
                    self._io.write_line(f"- {file}")

        return [package for package, _ in package_paths if package in changed_projects]

    def get_changed_external(self, ref: str) -> List["Package"]:
        old_graph = self.get_old_graph(ref)
        changed_external = []

        for package in self._graph:
            if self._graph.is_project_package(package):
                continue

            if not old_graph.has_package(package):
                changed_external.append(package)

        if self._io.is_very_verbose():
            self._io.write_line("Changed external packages:")
            for package in changed_external:
                self._io.write_line(f"- {package}")

        return changed_external

    def get_changed_files(self, ref: str) -> List[Path]:
        files = self._vcs.get_changed_files(ref)
        if self._io.is_very_verbose():
            self._io.write_line(f"Files changed since <info>{ref}</info>:")
            for file in files:
                self._io.write_line(f"- {file}")
        return files

    def get_old_graph(self, ref: str) -> DependencyGraph:
        old_pyproject_toml = self._vcs.read_file(ref, self._workspace.poetry.file.path)
        old_poetry_lock = self._vcs.read_file(ref, self._workspace.poetry.locker.lock.path)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            (temp_dir_path / "pyproject.toml").write_text(old_pyproject_toml)
            (temp_dir_path / "poetry.lock").write_text(old_poetry_lock)

            old_poetry = Factory().create_poetry(temp_dir_path)
            old_locked_repo = old_poetry.locker.locked_repository(with_dev_reqs=True)
            old_graph = DependencyGraph(old_locked_repo, [])

        return old_graph
