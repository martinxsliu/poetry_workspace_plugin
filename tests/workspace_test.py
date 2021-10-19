import tempfile
from pathlib import Path
from typing import Generator

import pytest
from cleo.io.null_io import NullIO
from poetry.core.pyproject.toml import PyProjectTOML
from poetry.factory import Factory

from poetry_workspace.errors import WorkspaceError
from poetry_workspace.workspace import Workspace
from tests.conftest import EXAMPLE_WORKSPACE_PYPROJECT_PATH

_PYPROJECT_PATH = Path(__file__).parent.parent / "example" / "pyproject.toml"


@pytest.fixture()
def non_workspace_pyproject() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as dir:
        path = Path(dir) / "pyproject.toml"
        path.write_text(
            """
[tool.poetry]
name = "normal"
version = "0.1.0"
description = ""
authors = ["Bob <bob@bob.com>"]

[tool.poetry.dependencies]
python = "^3.6"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
        )
        yield path


def test_workspace_with_non_project_pyproject(non_workspace_pyproject: Path) -> None:
    pyproject = PyProjectTOML(non_workspace_pyproject)
    with pytest.raises(WorkspaceError):
        Workspace(pyproject, NullIO())


def test_workspace_with_empty_workspace_section(non_workspace_pyproject: Path) -> None:
    non_workspace_pyproject.write_text(
        non_workspace_pyproject.read_text()
        + """
[tool.poetry.workspace]
"""
    )
    pyproject = PyProjectTOML(non_workspace_pyproject)
    with pytest.raises(WorkspaceError):
        Workspace(pyproject, NullIO())


def test_workspace_with_extra_workspace_section(non_workspace_pyproject: Path) -> None:
    non_workspace_pyproject.write_text(
        non_workspace_pyproject.read_text()
        + """
[tool.poetry.workspace]
extra_field = true
"""
    )
    pyproject = PyProjectTOML(non_workspace_pyproject)
    with pytest.raises(RuntimeError):
        Workspace(pyproject, NullIO())


def test_workspace_with_invalid_workspace_section(non_workspace_pyproject: Path) -> None:
    non_workspace_pyproject.write_text(
        non_workspace_pyproject.read_text()
        + """
[tool.poetry.workspace]
include = 123
"""
    )
    pyproject = PyProjectTOML(non_workspace_pyproject)
    with pytest.raises(RuntimeError):
        Workspace(pyproject, NullIO())


def test_normal_pyproject(non_workspace_pyproject: Path) -> None:
    poetry = Factory().create_poetry(non_workspace_pyproject.parent)
    assert poetry.package.name == "normal"


def test_poetry(example_workspace: Workspace) -> None:
    assert example_workspace.poetry
    assert example_workspace.poetry.package.name == "root"
    assert example_workspace.poetry.file.path == EXAMPLE_WORKSPACE_PYPROJECT_PATH


def test_projects(example_workspace: Workspace) -> None:
    assert example_workspace.projects
    assert [project.package.name for project in example_workspace.projects] == ["liba", "libb", "libc"]


def test_find_project(example_workspace: Workspace) -> None:
    assert example_workspace.find_project("liba")
    assert example_workspace.find_project("libb")
    assert example_workspace.find_project("libc")
    assert example_workspace.find_project("experimental") is None
    assert example_workspace.find_project("unknown") is None
