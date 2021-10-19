from pathlib import Path

import pytest

from poetry_workspace.errors import VCSError
from poetry_workspace.vcs.git import Git
from tests.vcs import git_util


@pytest.fixture()
def commit_1(git: Git) -> str:
    a_txt = Path("a.txt")
    assert not a_txt.exists()
    a_txt.write_text("1")

    return git_util.commit()


@pytest.fixture()
def commit_2(commit_1: str) -> str:
    a_txt = Path("a.txt")
    assert a_txt.read_text() == "1"
    a_txt.write_text("2")

    b_txt = Path("b.txt")
    assert not b_txt.exists()
    b_txt.write_text("2")

    return git_util.commit()


@pytest.fixture()
def commit_3(commit_2: str) -> str:
    a_txt = Path("a.txt")
    assert a_txt.read_text() == "2"
    a_txt.write_text("3")

    b_txt = Path("b.txt")
    assert b_txt.read_text() == "2"
    b_txt.write_text("3")

    c_txt = Path("c.txt")
    assert not c_txt.exists()
    c_txt.write_text("3")

    return git_util.commit()


def test_get_changed_files(git: Git, commit_1: str, commit_2: str, commit_3: str) -> None:
    a_txt = git.root / "a.txt"
    b_txt = git.root / "b.txt"
    c_txt = git.root / "c.txt"
    assert git.get_changed_files(commit_1) == [a_txt, b_txt, c_txt]
    assert git.get_changed_files(commit_2) == [a_txt, b_txt, c_txt]
    assert git.get_changed_files(commit_3) == []


def test_get_changed_files_unknown_ref(git: Git, commit_1: str) -> None:
    with pytest.raises(VCSError):
        git.get_changed_files("unknown_ref")


def test_read_file(git: Git, commit_1: str, commit_2: str, commit_3: str) -> None:
    a_txt = Path("a.txt")
    assert git.read_file(commit_1, a_txt) == "1"
    assert git.read_file(commit_2, a_txt) == "2"
    assert git.read_file(commit_3, a_txt) == "3"

    b_txt = Path("b.txt")
    assert git.read_file(commit_2, b_txt) == "2"
    assert git.read_file(commit_3, b_txt) == "3"

    c_txt = Path("c.txt")
    assert git.read_file(commit_3, c_txt) == "3"


def test_read_file_abs_path(git: Git, commit_1: str) -> None:
    a_txt = git.root / "a.txt"
    assert a_txt.is_absolute()
    assert git.read_file(commit_1, a_txt) == "1"


def test_read_file_unknown_ref(git: Git, commit_1: str) -> None:
    a_txt = Path("a.txt")
    assert a_txt.exists()
    with pytest.raises(VCSError):
        git.read_file("unknown_ref", a_txt)


def test_read_file_unknown_file(git: Git, commit_1: str) -> None:
    z_txt = Path("z.txt")
    assert not z_txt.exists()
    with pytest.raises(VCSError):
        git.read_file(commit_1, z_txt)
