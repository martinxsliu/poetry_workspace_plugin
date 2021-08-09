.PHONY: fmt
fmt:
	poetry run black poetry_workspace
	poetry run isort poetry_workspace

.PHONY: reinstall
reinstall:
	python install-poetry.py --uninstall || true
	python install-poetry.py --preview
	poetry plugin add $(shell pwd)

.PHONY: publish
publish:
	poetry build
	poetry publish # currently broken on 1.2.0, see: https://github.com/python-poetry/poetry/issues/4349
