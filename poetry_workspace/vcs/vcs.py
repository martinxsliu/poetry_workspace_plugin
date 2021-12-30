from pathlib import Path
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from cleo.io.io import IO


class VCS:
    def __init__(self, root: Path, io: "IO"):
        self._root = root.resolve()
        self._io = io

    @property
    def root(self) -> Path:
        return self._root

    def get_changed_files(self, ref: str) -> List[Path]:
        raise NotImplementedError()

    def read_file(self, ref: str, file: Path) -> str:
        raise NotImplementedError()
