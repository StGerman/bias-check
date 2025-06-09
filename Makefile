# Makefile for RAG Bias Analysis Demo
# Simple commands for development workflow

.PHONY: help install test lint format clean run-demo

help:  ## Show this help message
	@echo "RAG Bias Analysis Framework - Demo Commands"
	@echo "==========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies with Poetry
	poetry install
	@echo "✅ Dependencies installed. Run 'poetry shell' to activate virtual environment."

test:  ## Run all tests with pytest
	poetry run pytest -v --cov=. --cov-report=term-missing
	@echo "✅ Tests completed."

test-fast:  ## Run tests excluding slow integration tests
	poetry run pytest -v -m "not slow"
	@echo "✅ Fast tests completed."

lint:  ## Run all linting tools
	poetry run black --check .
	poetry run isort --check-only .
	poetry run flake8 .
	poetry run mypy .
	@echo "✅ Linting completed."

format:  ## Format code with black and isort
	poetry run black .
	poetry run isort .
	@echo "✅ Code formatted."

lint-fix:  ## Run linting tools and fix issues automatically
	poetry run black .
	poetry run isort .
	@echo "✅ Code auto-formatted."

check:  ## Run tests and linting together
	make format
	make lint
	make test
	@echo "✅ All checks passed."

clean:  ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	@echo "✅ Cleanup completed."

run-demo:  ## Run a basic demo of the bias analysis framework
	@echo "🚀 Running RAG Bias Analysis Demo..."
	@echo "Note: Set CLAUDE_API_KEY environment variable for real API calls"
	poetry run python demo_runner.py
	@echo "✅ Demo completed. Check demo_results.csv for output."

setup-dev:  ## Set up development environment from scratch
	@echo "Setting up development environment..."
	pip install poetry
	make install
	@echo "✅ Development environment ready!"
	@echo "Next steps:"
	@echo "  1. Run 'poetry shell' to activate virtual environment"
	@echo "  2. Set ANTHROPIC_API_KEY environment variable"
	@echo "  3. Run 'make test' to verify everything works"
	@echo "  4. Run 'make run-demo' to see the framework in action"

validate:  ## Validate project structure and dependencies
	@echo "Validating project structure..."
	@test -f pyproject.toml || (echo "❌ pyproject.toml missing" && exit 1)
	@test -f conftest.py || (echo "❌ conftest.py missing" && exit 1)
	@test -f test_rag_bias.py || (echo "❌ test file missing" && exit 1)
	@test -f .github/copilot-instructions.md || (echo "❌ copilot instructions missing" && exit 1)
	poetry check
	@echo "✅ Project structure validated."

# Cache management commands
clear-cache:  ## Clear API response cache
	@echo "🗑️ Clearing API response cache..."
	@rm -rf .cache/
	@echo "✅ Cache cleared"

cache-stats:  ## Show cache statistics
	@echo "📊 Cache Statistics:"
	@if [ -d ".cache" ]; then \
		echo "Cache directory exists: .cache/"; \
		if [ -f ".cache/api_responses.json" ]; then \
			echo "Cache file size: $$(du -h .cache/api_responses.json | cut -f1)"; \
			echo "Cached responses: $$(cat .cache/api_responses.json | python3 -c 'import json, sys; data = json.load(sys.stdin); print(len(data))')"; \
		else \
			echo "No cache file found"; \
		fi; \
	else \
		echo "No cache directory found"; \
	fi

run-demo-fresh:  ## Run demo with fresh cache (clears cache first)
	@echo "🚀 Running RAG Bias Analysis Demo with fresh cache..."
	$(MAKE) clear-cache
	$(MAKE) run-demo

# Development workflow shortcuts
dev-start: setup-dev validate  ## Complete development setup
dev-test: format lint test      ## Full development test cycle
dev-quick: format test-fast     ## Quick development test cycle
