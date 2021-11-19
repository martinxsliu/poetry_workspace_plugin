from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Iterator, List, Set

from poetry_workspace.errors import GraphError

if TYPE_CHECKING:
    from poetry.core.packages.package import Package
    from poetry.repositories import Repository


class DependencyGraph:
    _repo: "Repository"
    _internal_urls: Set[str]
    _deps: Dict["Package", List["Package"]]
    _rdeps: Dict["Package", List["Package"]]
    _levels: Dict["Package", int]
    _sorted: List["Package"]

    def __init__(self, repo: "Repository", internal_urls: List[str]):
        self._repo = repo
        self._internal_urls = set(internal_urls)
        self._deps = {}
        self._rdeps = {}

        # Ensure that all keys exist.
        for package in repo.packages:
            self._deps[package] = []
            self._rdeps[package] = []

        for package in repo.packages:
            for dep in package.all_requires:
                found = repo.find_packages(dep)
                if len(found) == 0:
                    raise ValueError(f"no packages found for dependency {dep.name}")
                if len(found) > 1:
                    raise ValueError(f"multiple packages found for dependency {dep.name}")

                self._deps[package].append(found[0])
                self._rdeps[found[0]].append(package)

        self._levels = topological_sort(self._deps, self._rdeps)

        sorted_levels = sorted(self._levels.items(), key=lambda pair: (pair[1], pair[0].name))
        self._sorted = [package for package, _level in sorted_levels]

    def __iter__(self) -> Iterator["Package"]:
        return iter(self._sorted)

    def __len__(self) -> int:
        return len(self._sorted)

    def has_package(self, package: "Package") -> bool:
        found = self._repo.find_packages(package.to_dependency())
        return len(found) > 0

    def is_project_package(self, package: "Package") -> bool:
        return package.source_url in self._internal_urls

    def dependencies(self, name: str) -> List["Package"]:
        return self._deps[self.find_package(name)]

    def reverse_dependencies(self, name: str) -> List["Package"]:
        return self._rdeps[self.find_package(name)]

    def search(
        self,
        package_names: List[str] = None,
        include_dependencies: bool = False,
        include_reverse_dependencies: bool = False,
        include_external: bool = False,
    ) -> List["Package"]:
        if package_names is None:
            if include_external:
                return self._sorted
            return [package for package in self._sorted if self.is_project_package(package)]

        selected = set()
        for name in package_names:
            selected.add(self.find_package(name))

        def add_dep(acc: Set["Package"], package: "Package", deps: Dict["Package", List["Package"]]) -> None:
            if package in acc:
                return
            acc.add(package)
            for dep in deps[package]:
                add_dep(acc, dep, deps)

        dependencies: Set["Package"] = set()
        if include_dependencies:
            for package in selected:
                add_dep(dependencies, package, self._deps)

        reverse_dependencies: Set["Package"] = set()
        if include_reverse_dependencies:
            for package in selected:
                add_dep(reverse_dependencies, package, self._rdeps)

        results = selected.union(dependencies).union(reverse_dependencies)
        if not include_external:
            results = {package for package in results if self.is_project_package(package)}

        return sorted(results, key=lambda package: (self._levels[package], package.name))

    def find_package(self, name: str) -> "Package":
        results = self._repo.search(name)
        if not results:
            raise GraphError(f"Project '{name}' is not in the dependency graph")
        return results[0]


def topological_sort(
    deps: Dict["Package", List["Package"]],
    rdeps: Dict["Package", List["Package"]],
) -> Dict["Package", int]:
    """
    Returns a dictionary mapping a package to its level. Levels are strictly
    negative integers that represent the maximum number of connections from
    the root to the package, e.g. -1 is the highest possible level and means
    that it is a direct dependency of the root and no other transitive package
    depends upon it.
    """
    levels: Dict["Package", int] = defaultdict(int)

    def iter(package: "Package", level: int) -> None:
        if levels[package] <= level:
            return
        levels[package] = level
        for dep in deps[package]:
            iter(dep, level - 1)

    for package, package_rdeps in rdeps.items():
        if len(package_rdeps) == 0:
            # Begin iteration at top level deps.
            iter(package, -1)

    return levels
