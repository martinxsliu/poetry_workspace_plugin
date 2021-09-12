from cleo.helpers import option
from poetry.console.commands.command import Command


class ReleaseCommand(Command):
    name = "release"
    description = "Bumps the version in <comment>pyproject.toml</comment>."

    options = [
        option("major", None, "Bump the major version."),
        option("minor", None, "Bump the minor version."),
        option("patch", None, "Bump the patch version."),
    ]

    def handle(self) -> int:
        if not self.poetry.pyproject.is_poetry_project():
            self.line("Not a valid Poetry project", style="error")
            return 1

        version = self.poetry.package.version
        if self.option("major"):
            bump = version.next_major()
        elif self.option("minor"):
            bump = version.next_minor()
        elif self.option("patch"):
            bump = version.next_patch()
        else:
            self.line("Please specify a version part to bump", style="error")
            return 1

        package = self.poetry.package
        self.line(f"Releasing <c1>{package.pretty_name}</c1> (<c2>{package.version}</c2> -> <c2>{str(bump)}</c2>)")

        self.poetry.pyproject.poetry_config["version"] = str(bump)
        self.poetry.pyproject.save()

        return 0
