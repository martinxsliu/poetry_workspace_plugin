from poetry.console.commands.build import BuildCommand as BaseBuildCommand


class BuildCommand(BaseBuildCommand):
    def handle(self) -> int:
        from poetry.core.packages.dependency import Dependency
        from poetry.core.packages.directory_dependency import DirectoryDependency
        from poetry.core.pyproject.toml import PyProjectTOML

        # Replace directory dependencies specified by a path with one specified
        # by a version constraint.
        for i, dep in enumerate(self.poetry.package.requires):
            if not isinstance(dep, DirectoryDependency):
                continue

            pyproject_toml = PyProjectTOML(dep.full_path / "pyproject.toml")
            if pyproject_toml.is_poetry_project():
                version = pyproject_toml.poetry_config.get("version")
                if not version:
                    self.io.write_line(
                        f"<warning>No version property in project {dep.full_path}, using version '*'</warning>"
                    )
                    version = "*"
            else:
                self.io.write_line(f"<warning>Not a Poetry project {dep.full_path}, using version '*'</warning>")
                version = "*"

            self.poetry.package.requires[i] = Dependency(
                name=dep.name,
                constraint=version,
                optional=dep.is_optional(),
                groups=list(dep.groups),
                allows_prereleases=dep.allows_prereleases(),
                extras=dep.extras,
                source_type=dep.source_type,
                source_url=dep.source_url,
                source_reference=dep.source_reference,
                source_resolved_reference=dep.source_resolved_reference,
            )

        return super().handle() or 0
