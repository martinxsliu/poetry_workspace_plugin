.PHONY: lint
lint:
	poetry run black --check poetry_workspace
	poetry run isort --check poetry_workspace
	poetry run mypy poetry_workspace

.PHONY: fmt
fmt:
	poetry run black poetry_workspace
	poetry run isort poetry_workspace

.PHONY: reinstall
reinstall:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python - --uninstall || true
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python - --preview
	poetry plugin add $(shell pwd)

.PHONY: publish
publish:
	poetry build
	poetry publish # currently broken on 1.2.0, see: https://github.com/python-poetry/poetry/issues/4349
