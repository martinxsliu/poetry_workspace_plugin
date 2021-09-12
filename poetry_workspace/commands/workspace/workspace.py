from typing import TYPE_CHECKING, List, Optional

from cleo.commands.command import Command
from cleo.helpers import option

from poetry_workspace.graph import DependencyGraph
from poetry_workspace.workspace import Workspace

if TYPE_CHECKING:
    from poetry.core.packages.package import Package
    from poetry.poetry import Poetry


class WorkspaceCommand(Command):
    options = [
        option("project", "p", "Select project name to include.", flag=False, multiple=True),
        option("include-dependencies", "d", "Include transitive dependencies of the selected projects."),
        option(
            "include-reverse-dependencies", "r", "Include projects that transitively depend on the selected projects."
        ),
        option("since", None, "Select projects that have changed since this reference.", flag=False),
    ]

    _workspace: Optional["Workspace"]
    _graph: Optional[DependencyGraph]

    def __init__(self) -> None:
        self._workspace = None
        self._graph = None

        super().__init__()

    @property
    def workspace(self) -> "Workspace":
        return self._workspace

    def set_workspace(self, workspace: "Workspace") -> None:
        self._workspace = workspace
        self._graph = None

    def handle(self) -> int:
        if not self.workspace:
            self.line("The 'workspace' command is only supported from within a workspace", style="error")
            return 1

        exit_code = self.pre_handle()
        if exit_code:
            return exit_code

        for project in self.selected_projects():
            poetry = self.workspace.find_project(project.name)
            if not poetry:
                self.line(f"Project {project.name} not found in workspace", style="error")
                return 1

            exit_code = self.handle_each(poetry)
            if exit_code:
                return exit_code

        exit_code = self.post_handle()
        if exit_code:
            return exit_code

        return 0

    def pre_handle(self) -> int:
        return 0

    def handle_each(self, poetry: "Poetry") -> int:
        """To be implemented by workspace subcommands."""
        raise NotImplementedError()

    def post_handle(self) -> int:
        return 0

    @property
    def graph(self) -> DependencyGraph:
        if self._graph is None:
            locked_repo = self.workspace.poetry.locker.locked_repository(with_dev_reqs=True)
            internal_urls = [str(project.file.path.parent) for project in self.workspace.projects]
            self._graph = DependencyGraph(locked_repo, internal_urls)
        return self._graph

    def selected_projects(self, include_external: bool = False) -> List["Package"]:
        if self.option("since"):
            if self.option("project"):
                self.line("Both --project and --since flags are provided, using --since", style="warning")
            return self.changed_projects(include_external)

        return self.graph.search(
            package_names=self.option("project"),
            include_dependencies=self.option("include-dependencies"),
            include_reverse_dependencies=self.option("include-reverse-dependencies"),
            include_external=include_external,
        )

    def changed_projects(self, include_external: bool = False) -> List["Package"]:
        from poetry_workspace.diff import Diff

        ref = self.option("since")

        diff = Diff(self.workspace, self.graph, io=self.io)
        changed = diff.get_changed_projects(ref)
        if self.option("include-reverse-dependencies"):
            changed.extend(diff.get_changed_external(ref))

        return self.graph.search(
            package_names=[package.name for package in changed],
            include_dependencies=self.option("include-dependencies"),
            include_reverse_dependencies=self.option("include-reverse-dependencies"),
            include_external=include_external,
        )
