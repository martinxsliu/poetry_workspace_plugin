from typing import TYPE_CHECKING, List, Optional

from cleo.commands.command import Command
from cleo.helpers import option

from poetry_workspace.graph import DependencyGraph
from poetry_workspace.workspace import Workspace

if TYPE_CHECKING:
    from poetry.core.packages.package import Package


class WorkspaceCommand(Command):
    options = [
        option("project", "p", "Select project name to include.", flag=False, multiple=True),
        option("include-dependencies", "d", "Include transitive dependencies of the selected projects."),
        option(
            "include-reverse-dependencies", "r", "Include projects that transitively depend on the selected projects."
        ),
        option("include-external", "e", "Include external dependencies not in the workspace."),
    ]

    _workspace: Optional["Workspace"]
    _graph: Optional[DependencyGraph]

    def __init__(self) -> None:
        self._workspace = None
        self._graph = None

        super(WorkspaceCommand, self).__init__()

    @property
    def workspace(self) -> "Workspace":
        return self._workspace

    def set_workspace(self, workspace: "Workspace") -> None:
        self._workspace = workspace

    @property
    def graph(self) -> DependencyGraph:
        if self._graph is None:
            locked_repo = self.workspace.poetry.locker.locked_repository(with_dev_reqs=True)
            internal_urls = [str(project.file.path.parent) for project in self.workspace.projects]
            self._graph = DependencyGraph(locked_repo, internal_urls)
        return self._graph

    def selected_projects(self) -> List["Package"]:
        return self.graph.search(
            self.option("project"),
            self.option("include-dependencies"),
            self.option("include-reverse-dependencies"),
            self.option("include-external"),
        )
