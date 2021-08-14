from cleo.helpers import argument, option

from poetry_workspace.commands.workspace.workspace import WorkspaceCommand


class WorkspaceChangedCommand(WorkspaceCommand):
    name = "workspace changed"
    description = "Lists changed projects."
    help = """
The <info>workspace list</> command lists projects in the workspace's dependency
graph. Use flags to optionally select a subset of projects, and to output
their dependencies, reverse dependencies, and whether to include projects
external to the workspace in the dependency list."""

    arguments = [
        argument("reference", "Projects that have changed since this reference."),
    ]
    options = [
        option("project", "p", "Check if project has changed.", flag=False, multiple=True),
        option("include-dependencies", "d", "Include transitive dependencies of the changed projects."),
        option(
            "include-reverse-dependencies", "r", "Include projects that transitively depend on the changed projects."
        ),
        option("include-external", "e", "Check for changes to external dependencies (requires --include-reverse-dependencies)."),
    ]

    def handle(self) -> int:
        from poetry_workspace.diff import Diff

        if not self.workspace:
            self.io.write_line("The 'workspace' command is only supported from within a workspace")
            return 1

        ref = self.argument("reference")
        if not ref:
            self.io.write_line("No reference specified")
            return 1

        diff = Diff(self.workspace, self.graph, io=self.io)
        changed = diff.get_changed_projects(ref)
        if self.option("include-external"):
            changed.extend(diff.get_changed_external(ref))

        changed_names = {package.name for package in changed}
        if self.option("project"):
            changed_names.intersection_update(set(self.option("project")))

        selected = self.graph.search(
            package_names=list(changed_names),
            include_dependencies=self.option("include-dependencies"),
            include_reverse_dependencies=self.option("include-reverse-dependencies"),
            include_external=False,
        )
        for package in selected:
            self.io.write_line(package.name)

        return 0
