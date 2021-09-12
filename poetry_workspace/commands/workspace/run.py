import os
import subprocess
from typing import TYPE_CHECKING

from cleo.helpers import option
from poetry.console.commands.env_command import EnvCommand
from poetry.console.commands.run import RunCommand

from poetry_workspace.commands.workspace.workspace import WorkspaceCommand

if TYPE_CHECKING:
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
        self._procs = []

    @property
    def parallel(self) -> str:
        return self.option("parallel")

    def handle_each(self, poetry: "Poetry") -> int:
        cmd = RunCommand()
        cmd.set_env(self.env)
        cmd.set_poetry(poetry)

        def execute(*args):
            command = self.env.get_command_from_bin(args[0]) + list(args[1:])
            env = dict(os.environ)

            kwargs = {
                "cwd": poetry.file.path.parent,
                "env": env,
            }
            if self.parallel:
                kwargs["stdout"] = subprocess.PIPE
                kwargs["stderr"] = subprocess.PIPE
                kwargs["text"] = True

            proc = subprocess.Popen(command, **kwargs)
            if self.parallel:
                self._procs.append(proc)
            else:
                proc.communicate()
                return proc.returncode

        cmd.env.execute = execute
        return cmd.execute(self.io)

    def post_handle(self) -> int:
        if not self.parallel:
            return 0

        for proc in self._procs:
            stdout, stderr = proc.communicate()
            if stdout:
                self.line(stdout)
            if stderr:
                self.line(stderr)
            exit_code = proc.returncode
            if exit_code:
                return exit_code
