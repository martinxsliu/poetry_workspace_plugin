import pytest
from poetry.core.packages.package import Package

from poetry_workspace.errors import GraphError
from poetry_workspace.graph import DependencyGraph
from tests.conftest import assert_packages, build_repo


@pytest.fixture()
def graph() -> DependencyGraph:
    repo = build_repo(
        {
            "external/ext": [],
            "internal/a": ["ext"],
            "internal/b": ["a"],
            "internal/c": ["b"],
        }
    )
    return DependencyGraph(repo, ["internal"])


def test_iter(graph: DependencyGraph) -> None:
    packages = list(graph)
    assert packages
    assert [package.name for package in packages] == ["ext", "a", "b", "c"]


def test_len(graph: DependencyGraph) -> None:
    assert len(graph) == 4


def test_has_package(graph: DependencyGraph) -> None:
    assert graph.has_package(Package("ext", "1.0")) is True
    assert graph.has_package(Package("a", "1.0")) is True

    # Different version
    assert graph.has_package(Package("a", "2.0")) is False

    # Unknown package
    assert graph.has_package(Package("z", "1.0")) is False


def test_find_package(graph: DependencyGraph) -> None:
    assert graph.find_package("ext").name == "ext"
    assert graph.find_package("a").name == "a"

    with pytest.raises(GraphError):
        assert graph.find_package("z") is None


def test_is_project_package(graph: DependencyGraph) -> None:
    def is_project_package(name: str) -> bool:
        package = graph.find_package(name)
        return graph.is_project_package(package)

    assert is_project_package("ext") is False
    assert is_project_package("a") is True


def test_dependencies(graph: DependencyGraph) -> None:
    assert_packages(graph.dependencies("ext"), [])
    assert_packages(graph.dependencies("a"), ["ext"])
    assert_packages(graph.dependencies("b"), ["a"])
    assert_packages(graph.dependencies("c"), ["b"])


def test_reverse_dependencies(graph: DependencyGraph) -> None:
    assert_packages(graph.reverse_dependencies("ext"), ["a"])
    assert_packages(graph.reverse_dependencies("a"), ["b"])
    assert_packages(graph.reverse_dependencies("b"), ["c"])
    assert_packages(graph.reverse_dependencies("c"), [])


def test_search(graph: DependencyGraph) -> None:
    assert_packages(graph.search(), ["a", "b", "c"])
    assert_packages(graph.search(include_external=True), ["ext", "a", "b", "c"])
    assert_packages(graph.search(package_names=["b"]), ["b"])
    assert_packages(graph.search(package_names=["b"], include_dependencies=True), ["a", "b"])
    assert_packages(
        graph.search(package_names=["b"], include_dependencies=True, include_external=True), ["ext", "a", "b"]
    )
    assert_packages(graph.search(package_names=["b"], include_reverse_dependencies=True), ["b", "c"])
    assert_packages(
        graph.search(
            package_names=["b"], include_dependencies=True, include_reverse_dependencies=True, include_external=True
        ),
        ["ext", "a", "b", "c"],
    )
