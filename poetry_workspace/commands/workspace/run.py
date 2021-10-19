import os
import subprocess
from typing import TYPE_CHECKING, List, Tuple

from cleo.helpers import option
from poetry.console.commands.env_command import EnvCommand
from poetry.console.commands.run import RunCommand

from poetry_workspace.commands.workspace.workspace import WorkspaceCommand

if TYPE_CHECKING:
    from cleo.io.io import IO
    from poetry.poetry import Poetry


class WorkspaceRunCommand(WorkspaceCommand, EnvCommand):
    name = "workspace run"
    description = "Runs a command for each workspace project."

    options = [
        option("parallel", None, "Run all commands immediately."),
    ] + WorkspaceCommand.options
    arguments = RunCommand.arguments

    def __init__(self):
        super().__init__()

        # Used in parallel mode.
        self._procs: List[Tuple[subprocess.Popen, "IO"]] = []

    @property
    def parallel(self) -> str:
        return self.option("parallel")

    def handle_each(self, poetry: "Poetry", io: "IO") -> int:
        cmd = RunCommand()
        cmd.set_env(self.env)
        cmd.set_poetry(poetry)

        def execute(*args):
            command = self.env.get_command_from_bin(args[0]) + list(args[1:])
            env = dict(os.environ)

            proc = subprocess.Popen(
                args=command,
                cwd=poetry.file.path.parent,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if self.parallel:
                self._procs.append((proc, io))
            else:
                return self._communicate(proc, io)

        cmd.env.execute = execute
        return cmd.execute(io)

    def post_handle(self) -> int:
        if not self.parallel:
            return 0

        for proc, io in self._procs:
            exit_code = self._communicate(proc, io)
            if exit_code:
                return exit_code

        return 0

    def _communicate(self, proc: subprocess.Popen, io: "IO") -> int:
        stdout, stderr = proc.communicate()
        if stdout:
            io.write_line(stdout.strip())
        if stderr:
            io.write_line(stderr.strip())
        return proc.returncode
