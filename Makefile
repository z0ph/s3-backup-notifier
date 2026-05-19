.DEFAULT_GOAL := help

PROJECT ?= s3-monitor
ENV     ?= dev

.PHONY: help build deploy destroy lint test clean

help:
	@echo "${PROJECT}"
	@echo ""
	@echo "  build    - sam build"
	@echo "  deploy   - sam deploy --config-env $${ENV} (default: dev)"
	@echo "  destroy  - sam delete the stack for $${ENV}"
	@echo "  lint     - ruff check ."
	@echo "  test     - pytest"
	@echo "  clean    - remove local build artifacts"

build:
	sam build

deploy: build
	sam deploy --config-env $(ENV)

destroy:
	@read -p "Destroy stack '$(PROJECT)-$(ENV)'? [y/N]: " sure && [ $${sure:-N} = 'y' ]
	sam delete --config-env $(ENV) --stack-name $(PROJECT)-$(ENV) --no-prompts

lint:
	ruff check .

test:
	pytest

clean:
	@rm -fr .aws-sam/ build/ dist/ htmlcov/ .eggs/ .tox/ .pytest_cache/ .ruff_cache/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '.DS_Store' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +
