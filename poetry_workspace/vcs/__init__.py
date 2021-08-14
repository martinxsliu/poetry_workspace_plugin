from pathlib import Path

from poetry_workspace.errors import VCSError
from poetry_workspace.vcs.vcs import VCS


def detect_vcs() -> VCS:
    cwd = Path.cwd()
    for dir_path in [cwd] + list(cwd.parents):
        if (dir_path / ".git").is_dir():
            from poetry_workspace.vcs.git import Git

            return Git(dir_path)

    raise VCSError("unable to detect VCS type")
