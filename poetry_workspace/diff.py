import tempfile
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from poetry.core.pyproject.toml import PyProjectTOML
from poetry.packages.locker import Locker

from poetry_workspace.errors import VCSError
from poetry_workspace.graph import DependencyGraph
from poetry_workspace.vcs import VCS, detect_vcs
from poetry_workspace.workspace import Workspace

if TYPE_CHECKING:
    from cleo.io.io import IO
    from poetry.core.packages.package import Package


class Diff:
    _workspace: Workspace
    _vcs: VCS
    _io: "IO"

    def __init__(self, workspace: Workspace, vcs: VCS = None, io: "IO" = None):
        if io is None:
            from cleo.io.null_io import NullIO

            io = NullIO()

        self._workspace = workspace
        self._vcs = vcs or detect_vcs(io)
        self._io = io

    def get_changed_projects(self, ref: str) -> List["Package"]:
        package_paths = [(package, Path(package.source_url)) for package in self._workspace.graph.search()]

        def find_parent_project(file_path: Path) -> Optional["Package"]:
            for package, package_path in package_paths:
                try:
                    file_path.relative_to(package_path)
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

        if self._io.is_debug():
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

        for package in self._workspace.graph:
            if self._workspace.graph.is_project_package(package):
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
        if self._io.is_debug():
            self._io.write_line(f"Files changed since <info>{ref}</info>:")
            for file in files:
                self._io.write_line(f"- {file}")
        return files

    def get_old_graph(self, ref: str) -> DependencyGraph:
        old_pyproject_toml = self._vcs.read_file(ref, self._workspace.poetry.file.path)
        old_poetry_lock = self._vcs.read_file(ref, self._workspace.poetry.locker.lock.path)

        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)
            (dir_path / "pyproject.toml").write_text(old_pyproject_toml)
            (dir_path / "poetry.lock").write_text(old_poetry_lock)

            local_config = PyProjectTOML(path=dir_path / "pyproject.toml").poetry_config
            locker = Locker(dir_path / "poetry.lock", local_config)
            workspace_dir = self._workspace.poetry.file.parent

            # When creating the locked repository below, Poetry expects to find the
            # pyproject.toml or setup.py file for each of the directory dependencies.
            # Here we iterate through the lock file and try to populate those package
            # files from the old VCS reference.
            for package_info in locker.lock_data["package"]:
                source = package_info.get("source", {})
                if source.get("type") != "directory":
                    continue

                package_path = Path(source.get("url")) / "pyproject.toml"
                package_contents = None
                try:
                    package_contents = self._vcs.read_file(ref, workspace_dir / package_path)
                except VCSError:
                    pass

                if not package_contents:
                    package_path = Path(source.get("url")) / "setup.py"
                    try:
                        package_contents = self._vcs.read_file(ref, workspace_dir / package_path)
                    except VCSError:
                        pass

                if not package_contents:
                    raise VCSError(f"package {package_info['name']} at {ref} does not seem to be a Python package")

                temp_package_path = temp_dir / package_path
                temp_package_path.parent.mkdir(parents=True)
                temp_package_path.write_text(package_contents)

            locked_repo = locker.locked_repository(with_dev_reqs=True)
            return DependencyGraph(locked_repo, [])
