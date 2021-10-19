from tests.conftest import run


def commit() -> str:
    run("git", "add", ".")
    run("git", "commit", "-m", "commit")
    return run("git", "rev-parse", "HEAD")
