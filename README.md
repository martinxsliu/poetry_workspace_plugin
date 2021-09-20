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
