from pathlib import Path
from typing import List


class VCS:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def get_changed_files(self, ref: str) -> List[Path]:
        raise NotImplementedError()

    def read_file(self, ref: str, file: Path) -> str:
        raise NotImplementedError()
