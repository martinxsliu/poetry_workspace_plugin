# Poetry Workspace Plugin

This experimental tool is a [Poetry Plugin](https://python-poetry.org/docs/master/plugins) to support workflows in a multi-project repository.

## Installation

Make sure you are using at least Poetry 1.2.0a2. To install this preview release, run:

```shell
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python - --preview
```

Install this plugin:

```shell
poetry plugin add poetry-workspace-plugin
```

## Workspace

A workspace is a collection of Poetry projects that share a single environment.

## Example config to place at the root
[tool.poetry]
name = "code"
version = "0.1.0"
description = "Opendoor Python workspace"
authors = ["Developers <developers@opendoor.com>"]

[[tool.poetry.source]]
name = "pypi-local"
url = "https://opendoor.jfrog.io/opendoor/api/pypi/pip/simple"
secondary = true

[tool.poetry.workspace]
include = [
  "lib/**",
  "workspace/**",
]
exclude = [
  "lib/dev-tools",
  "lib/legacy",
  "lib/template/**",
]

# IMPORTANT: This pyproject.toml file declares dependencies for the shared Python
# workspace. If your app does not belong to the
# workspace (i.e. not included in the `include` section above) then do not add your
# app dependencies here, it will have no effect. Even if your app does belong to
# the workspace, prefer adding app specific dependencies in your app's project. This
# section is reserved for workspace level constraints.
[tool.poetry.dependencies]
python = "~3.9"
virtualenv = "^20.10.0"

[tool.poetry.dev-dependencies]
"opendoor.dev-tools" = {path = "lib/dev-tools", develop = true}
"opendoor.tools" = {path = "tools", develop = true}
