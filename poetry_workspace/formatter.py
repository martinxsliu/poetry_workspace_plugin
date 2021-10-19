from cleo.formatters.formatter import Formatter


class WorkspaceFormatter(Formatter):
    def __init__(self, prefix: str, *args, **kwargs):
        self._prefix = prefix
        super().__init__(*args, **kwargs)

    def format(self, message: str) -> str:
        lines = message.split("\n")
        return super().format("\n".join(f"<c2>{self._prefix}></> {line}" for line in lines))
