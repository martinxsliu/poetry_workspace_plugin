import subprocess
from pathlib import Path
from typing import List

from cleo.io.outputs.output import Verbosity

from poetry_workspace.errors import VCSError
from poetry_workspace.vcs.vcs import VCS


class Git(VCS):
    def get_changed_files(self, ref: str) -> List[Path]:
        commands = ["git", "diff", "--name-only", ref]
        self._io.write_line(f"Running command: <comment>{' '.join(commands)}</>", verbosity=Verbosity.VERY_VERBOSE)

        try:
            proc = subprocess.run(commands, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise VCSError(f"git command failed:\n\n{e.stderr.decode()}")

        return [self._root / file for file in proc.stdout.decode().split()]

    def read_file(self, ref: str, file: Path) -> str:
        if file.is_absolute():
            file = file.relative_to(self._root)

        commands = ["git", "show", f"{ref}:{file}"]
        self._io.write_line(f"Running command: <comment>{' '.join(commands)}</>", verbosity=Verbosity.VERY_VERBOSE)

        try:
            proc = subprocess.run(commands, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise VCSError(f"git command failed:\n\n{e.stderr.decode()}")

        return proc.stdout.decode()
