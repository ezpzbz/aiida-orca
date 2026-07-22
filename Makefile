.PHONY: install
install: ## Install the virtual environment and pre-commit hooks
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools
	@uv lock --locked
	@uv run pre-commit run -a
	@uv run mypy aiida_orca/calculations/orca_orca.py aiida_orca/parsers/__init__.py aiida_orca/utils/input_generator.py aiida_orca/workchains/base.py

.PHONY: test
test: ## Run the test suite
	@uv run pytest tests

.PHONY: build
build: ## Build wheel and sdist
	@uv build

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
