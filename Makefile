.PHONY: install dev test lint format clean build docs run dashboard help
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip
VENV := venv
VENV_BIN := $(VENV)/bin
PYTHON_VENV := $(VENV_BIN)/python
PIP_VENV := $(VENV_BIN)/pip

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)DLQ Monitor Development Tools$(NC)"
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	@echo "$(GREEN)Installing production dependencies...$(NC)"
	$(PIP) install -r requirements.txt

dev: $(VENV) ## Setup development environment with dev dependencies
	@echo "$(GREEN)Setting up development environment...$(NC)"
	$(PIP_VENV) install -r requirements.txt
	$(PIP_VENV) install pytest pytest-cov black isort ruff mypy types-requests types-pyyaml pre-commit
	$(VENV_BIN)/pre-commit install
	@echo "$(GREEN)Development environment ready!$(NC)"
	@echo "Activate with: source $(VENV)/bin/activate"

$(VENV):
	@echo "$(GREEN)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)

test: ## Run pytest with coverage
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	pytest --cov=src --cov-report=html --cov-report=term-missing tests/
	@echo "$(GREEN)Coverage report generated in htmlcov/$(NC)"

test-quick: ## Run tests without coverage
	@echo "$(GREEN)Running quick tests...$(NC)"
	pytest tests/ -v

lint: ## Run ruff and mypy
	@echo "$(GREEN)Running ruff linter...$(NC)"
	ruff check src/ tests/ --fix
	@echo "$(GREEN)Running mypy type checker...$(NC)"
	mypy src/ --ignore-missing-imports

format: ## Run black and isort
	@echo "$(GREEN)Formatting code with black...$(NC)"
	black src/ tests/ *.py
	@echo "$(GREEN)Sorting imports with isort...$(NC)"
	isort src/ tests/ *.py

clean: ## Clean build artifacts and cache
	@echo "$(GREEN)Cleaning build artifacts and cache...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete

build: clean ## Build package distribution
	@echo "$(GREEN)Building package distribution...$(NC)"
	$(PYTHON) -m build

docs: ## Build documentation
	@echo "$(GREEN)Building documentation...$(NC)"
	@if [ -d "docs/" ]; then \
		cd docs && make html; \
		echo "$(GREEN)Documentation built in docs/_build/html/$(NC)"; \
	else \
		echo "$(YELLOW)No docs directory found. Create sphinx docs with: sphinx-quickstart docs$(NC)"; \
	fi

run: ## Run the main monitor in production mode
	@echo "$(GREEN)Starting DLQ monitor in production mode...$(NC)"
	./start_monitor.sh production

dashboard: ## Launch the enhanced dashboard
	@echo "$(GREEN)Launching enhanced dashboard...$(NC)"
	./start_monitor.sh enhanced

ultimate: ## Launch the ultimate monitor dashboard
	@echo "$(GREEN)Launching ultimate monitor dashboard...$(NC)"
	./start_monitor.sh ultimate

discover: ## Discover all DLQ queues
	@echo "$(GREEN)Discovering DLQ queues...$(NC)"
	./start_monitor.sh discover

test-notify: ## Test notification system
	@echo "$(GREEN)Testing notification system...$(NC)"
	./start_monitor.sh notification-test

test-voice: ## Test ElevenLabs voice
	@echo "$(GREEN)Testing ElevenLabs voice...$(NC)"
	./start_monitor.sh voice-test

test-claude: ## Test Claude Code integration
	@echo "$(GREEN)Testing Claude Code integration...$(NC)"
	./start_monitor.sh test-claude

status: ## Check Claude investigation status
	@echo "$(GREEN)Checking Claude investigation status...$(NC)"
	./start_monitor.sh status

logs: ## Tail investigation logs
	@echo "$(GREEN)Tailing investigation logs...$(NC)"
	./start_monitor.sh logs

setup-env: ## Create .env file from template
	@if [ ! -f .env ]; then \
		if [ -f .env.template ]; then \
			cp .env.template .env; \
			echo "$(GREEN).env file created from template$(NC)"; \
			echo "$(YELLOW)Please edit .env and add your credentials$(NC)"; \
		else \
			echo "$(RED)No .env.template found$(NC)"; \
		fi \
	else \
		echo "$(YELLOW).env file already exists$(NC)"; \
	fi

check-deps: ## Check for outdated dependencies
	@echo "$(GREEN)Checking for outdated dependencies...$(NC)"
	pip list --outdated

security: ## Run security checks
	@echo "$(GREEN)Running security checks...$(NC)"
	pip install bandit safety
	bandit -r src/
	safety check

pre-commit-all: ## Run pre-commit on all files
	@echo "$(GREEN)Running pre-commit on all files...$(NC)"
	pre-commit run --all-files

install-hooks: ## Install git hooks
	@echo "$(GREEN)Installing git hooks...$(NC)"
	pre-commit install

# Development workflow shortcuts
dev-setup: dev setup-env ## Complete development setup
	@echo "$(GREEN)Development setup complete!$(NC)"

qa: format lint test ## Run quality assurance checks (format, lint, test)
	@echo "$(GREEN)Quality assurance checks completed!$(NC)"

ci: lint test ## Run CI checks (lint and test)
	@echo "$(GREEN)CI checks completed!$(NC)"