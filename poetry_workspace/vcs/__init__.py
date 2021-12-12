from pathlib import Path
from typing import TYPE_CHECKING

from poetry_workspace.errors import VCSError
from poetry_workspace.vcs.vcs import VCS

if TYPE_CHECKING:
    from cleo.io.io import IO


def detect_vcs(io: "IO") -> VCS:
    cwd = Path.cwd()
    for dir_path in [cwd] + list(cwd.parents):
        if (dir_path / ".git").is_dir():
            from poetry_workspace.vcs.git import Git

            return Git(dir_path, io)

    raise VCSError("unable to detect VCS type")
