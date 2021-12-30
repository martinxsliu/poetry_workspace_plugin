import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Dict, Generator, List

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
    return Git(temp_dir, NullIO())


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


def run(*args: str) -> str:
    proc = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.stdout.decode().strip()


def assert_run_errors(*args: str, pattern: str = None) -> None:
    try:
        run(*args)
    except subprocess.CalledProcessError as e:
        if pattern:
            assert re.search(pattern, e.stderr.decode())
    else:
        pytest.fail(f"expected command to fail: {' '.join(args)}")


def sync_dir(src: Path, dst: Path) -> None:
    if not src.is_dir():
        raise ValueError(f"source {src} is not a directory")
    if not dst.is_dir():
        raise ValueError(f"destination {dst} is not a directory")

    # First, clear up dst directory.
    for name in os.listdir(dst):
        if name in (".git"):
            continue

        path = dst / name
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    # Now copy over all contents of src.
    for name in os.listdir(src):
        if name in (".venv", "__pycache__"):
            continue

        src_path = src / name
        dst_path = dst / name
        if os.path.isfile(src_path) or os.path.islink(src_path):
            shutil.copyfile(src_path, dst_path)
        elif os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)


@pytest.fixture()
def create_fixture_workspace(temp_dir: Path) -> Callable[[str], Path]:
    def create(fixture_relative_path: str) -> Path:
        sync_dir(Path(__file__).parent / "fixtures" / fixture_relative_path, temp_dir)
        return temp_dir

    return create
