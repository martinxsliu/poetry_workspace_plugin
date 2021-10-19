import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Generator, List

import pytest
from cleo.io.null_io import NullIO
from poetry.core.packages.dependency import Dependency
from poetry.core.packages.package import Package
from poetry.core.pyproject.toml import PyProjectTOML
from poetry.repositories import Repository

from poetry_workspace.vcs.git import Git
from poetry_workspace.workspace import Workspace

EXAMPLE_WORKSPACE_PYPROJECT_PATH = Path(__file__).parent.parent / "example" / "pyproject.toml"


@pytest.fixture()
def example_workspace() -> Workspace:
    pyproject = PyProjectTOML(EXAMPLE_WORKSPACE_PYPROJECT_PATH)
    return Workspace(pyproject, NullIO())


@pytest.fixture()
def temp_dir() -> Generator[Path, None, None]:
    old_cwd = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    yield Path(temp_dir).resolve()
    os.chdir(old_cwd)
    shutil.rmtree(temp_dir)


@pytest.fixture()
def git(temp_dir: Path) -> Git:
    run("git", "init")
    return Git(temp_dir)


def build_repo(deps: Dict[str, List[str]]) -> Repository:
    packages: List[Package] = []
    for package_spec, package_deps in deps.items():
        parts = package_spec.split("/")
        source = parts[0] if len(parts) > 0 else None
        name = parts[-1]
        package = Package(name, "1.0", source_url=source)
        for dep in package_deps:
            package.add_dependency(Dependency(dep, "*"))
        packages.append(package)
    return Repository(packages)


def assert_packages(packages: List[Package], names: List[str]) -> None:
    assert [package.name for package in packages] == names


def run(*args) -> str:
    proc = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.stdout.decode().strip()
