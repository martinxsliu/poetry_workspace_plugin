from pathlib import Path

import pytest
from cleo.io.null_io import NullIO
from poetry.core.packages.package import Package
from poetry.core.pyproject.toml import PyProjectTOML

from poetry_workspace.diff import Diff
from poetry_workspace.vcs.git import Git
from poetry_workspace.workspace import Workspace
from tests.conftest import assert_packages, sync_dir
from tests.vcs import git_util


@pytest.fixture()
def commit_1(git: Git) -> str:
    sync_dir(Path(__file__).parent / "fixtures" / "diff" / "commit_1", git.root)
    return git_util.commit()


@pytest.fixture()
def commit_2(git: Git, commit_1: str) -> str:
    sync_dir(Path(__file__).parent / "fixtures" / "diff" / "commit_2", git.root)
    return git_util.commit()


@pytest.fixture()
def diff(git: Git, commit_2: str) -> Diff:
    pyproject = PyProjectTOML(git.root / "pyproject.toml")
    workspace = Workspace(pyproject, NullIO())
    return Diff(workspace=workspace, vcs=git)


def test_get_changed_projects(diff: Diff, commit_1: str) -> None:
    # liba is untouched, libb had its source code changed, and libc is a new package.
    assert_packages(diff.get_changed_projects(commit_1), ["libb", "libc"])


def test_get_changed_external(diff: Diff, commit_1: str) -> None:
    # pytz has been updated, but pytzdata is unchanged.
    assert_packages(diff.get_changed_external(commit_1), ["pytz"])


def test_get_changed_files(git: Git, diff: Diff, commit_1: str) -> None:
    changed_files_paths = diff.get_changed_files(commit_1)
    assert [str(path.relative_to(git.root)) for path in changed_files_paths] == [
        "poetry.lock",
        "projects/libb/libb/__init__.py",
        "projects/libb/pyproject.toml",
        "projects/libc/libc/__init__.py",
        "projects/libc/pyproject.toml",
    ]


def test_get_old_graph(diff: Diff, commit_1: str) -> None:
    graph = diff.get_old_graph(commit_1)
    assert graph.has_package(Package("pytz", "2020.1"))
    assert not graph.has_package(Package("pytz", "2020.5"))
