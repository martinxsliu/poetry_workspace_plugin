from typing import TYPE_CHECKING, List

from cleo.helpers import option

from poetry_workspace.commands.workspace.workspace import WorkspaceCommand

if TYPE_CHECKING:
    from poetry.core.packages.package import Package

_FORMATS = (
    "topological",
    "json",
    "tree",
)


class WorkspaceListCommand(WorkspaceCommand):
    name = "workspace list"
    description = "Lists workspace projects and their dependencies."
    help = """
The <info>workspace list</> command lists projects in the workspace's dependency
graph. Use flags to optionally select a subset of projects, and to output
their dependencies, reverse dependencies, and whether to include projects
external to the workspace in the dependency list."""

    options = [
        option("output", "o", f"Output format ({', '.join(_FORMATS)}).", flag=False, default=_FORMATS[0]),
        option("show-external", None, "Show external dependencies in the output."),
    ] + WorkspaceCommand.options

    def __init__(self):
        super().__init__()

        # Used for json and tree output formats.
        self._project_tree = {}

    @property
    def output(self) -> str:
        return self.option("output")

    @property
    def show_external(self) -> bool:
        return self.option("show-external")

    def handle(self) -> int:
        if not self.workspace:
            self.line("The 'workspace' command is only supported from within a workspace", style="error")
            return 1

        if self.output not in _FORMATS:
            self.line("unknown output format", style="error")
            return 1

        for project in self.selected_projects():
            if self.output == "topological":
                self.line(project.name)
                continue

            def get_tree(package_name: str) -> dict:
                deps = self.workspace.graph.dependencies(package_name)
                if not self.show_external:
                    deps = [dep for dep in deps if self.workspace.graph.is_project_package(dep)]
                return {dep.name: get_tree(dep.name) for dep in deps}

            self._project_tree[project.name] = get_tree(project.name)

        if self.output == "json":
            import json

            self.line(json.dumps(self._project_tree, indent=2))
        elif self.output == "tree":
            for project_name, tree in self._project_tree.items():
                self.write_tree(project_name, tree, [])
                self.line("")

        return 0

    def write_tree(self, project_name: str, tree: dict, last_levels: List[bool]) -> None:
        for i, is_last in enumerate(last_levels):
            if i != len(last_levels) - 1:
                if not is_last:
                    self.io.write("│   ")
                else:
                    self.io.write("    ")
            else:
                if not is_last:
                    self.io.write("├── ")
                else:
                    self.io.write("└── ")

        self.line(project_name)
        for i, (dep_name, dep_tree) in enumerate(tree.items()):
            self.write_tree(dep_name, dep_tree, last_levels + [i == len(tree) - 1])

    def selected_projects(self, *args) -> List["Package"]:
        projects = super().selected_projects(self.show_external)
        if self.output in ("json", "tree"):
            projects = sorted(projects, key=lambda project: project.name)
        return projects
