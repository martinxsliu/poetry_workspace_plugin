from pathlib import Path
from typing import Callable

from tests.conftest import assert_run_errors, run


def test_resolve_dependencies_directly(create_fixture_workspace: Callable[[str], Path]) -> None:
    dir_path = create_fixture_workspace("lock/resolve_dependencies_directly")
    run("poetry", "lock", "--no-update")

    # Change liba's pytz dependency to something unsolvable.
    pyproject_toml = dir_path / "projects" / "liba" / "pyproject.toml"
    contents = pyproject_toml.read_text()
    contents = contents.replace('pytz = ">=2019,<2021"', 'pytz = ">2021"')
    pyproject_toml.write_text(contents)

    assert_run_errors("poetry", "lock", "--no-update", pattern="version solving failed")
