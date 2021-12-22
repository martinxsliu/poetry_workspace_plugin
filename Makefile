.PHONY: install
install:
	rm -rf .venv
	poetry install

.PHONY: test
test:
	poetry run pytest tests

.PHONY: lint
lint:
	poetry run black --check poetry_workspace tests
	poetry run isort --check poetry_workspace tests
	poetry run mypy poetry_workspace tests

.PHONY: fmt
fmt:
	poetry run black poetry_workspace tests
	poetry run isort poetry_workspace tests

.PHONY: publish
publish:
	poetry build
	poetry publish # currently broken on 1.2.0, see: https://github.com/python-poetry/poetry/issues/4349
