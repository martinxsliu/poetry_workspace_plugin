from poetry_workspace.commands.workspace.workspace import WorkspaceCommand


class WorkspaceListCommand(WorkspaceCommand):
    name = "workspace list"
    description = "Lists projects and their dependencies."
    help = """
The <info>workspace list</> command lists projects in the workspace's dependency
graph. Use flags to optionally select a subset of projects, and to output
their dependencies, reverse dependencies, and whether to include projects
external to the workspace in the dependency list."""

    def handle(self) -> int:
        if not self.workspace:
            self.io.write_line("The 'workspace' command is only supported from within a workspace")
            return 1

        for package in self.selected_projects():
            self.io.write_line(package.name)

        return 0
