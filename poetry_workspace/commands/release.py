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
            self.io.write_line("<error>Not a valid Poetry project</error>")
            return 1

        version = self.poetry.package.version
        if self.option("major"):
            bump = version.next_major()
        elif self.option("minor"):
            bump = version.next_minor()
        elif self.option("patch"):
            bump = version.next_patch()
        else:
            self.io.write_line("<error>Please specify a version part to bump</error>")
            return 1

        self.poetry.pyproject.poetry_config["version"] = str(bump)
        self.poetry.pyproject.save()

        return 0
