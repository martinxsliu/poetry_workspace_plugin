import subprocess
from pathlib import Path
from typing import List

from poetry_workspace.errors import VCSError
from poetry_workspace.vcs.vcs import VCS


class Git(VCS):
    def get_changed_files(self, ref: str) -> List[Path]:
        try:
            proc = subprocess.run(
                ["git", "diff", "--name-only", ref], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            raise VCSError(f"git command failed:\n\n{e.stderr.decode()}")

        return [self.root / file for file in proc.stdout.decode().split()]

    def read_file(self, ref: str, file: Path) -> str:
        if file.is_absolute():
            file = file.relative_to(self.root)

        try:
            proc = subprocess.run(
                ["git", "show", f"{ref}:{file}"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            raise VCSError(f"git command failed:\n\n{e.stderr.decode()}")

        return proc.stdout.decode()
