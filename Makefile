.PHONY: help setup test lint format type-check clean run build install-hooks

help:
	@echo "CAN Pro-Decoder Development Commands"
	@echo "====================================="
	@echo "  make setup          - Set up development environment"
	@echo "  make install-hooks  - Install pre-commit hooks"
	@echo "  make run            - Run the application"
	@echo "  make test           - Run tests with coverage"
	@echo "  make test-quick     - Run tests without coverage"
	@echo "  make lint           - Check code with Ruff"
	@echo "  make format         - Format code with Black"
	@echo "  make type-check     - Type check with Mypy"
	@echo "  make quality        - Run all quality checks (lint, type-check, format-check)"
	@echo "  make build          - Build Windows executable"
	@echo "  make clean          - Clean build artifacts"

setup:
	python setup_dev.py

install-hooks:
	pre-commit install

run:
	python main.py

test:
	pytest -v --cov=. --cov-report=html --cov-report=term-missing

test-quick:
	pytest -v

lint:
	ruff check . --fix

format:
	black .

format-check:
	black --check .

type-check:
	mypy .

quality: lint type-check format-check
	@echo "Quality checks complete!"

build:
	python build_exe.py

clean:
	rm -rf dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

.DEFAULT_GOAL := help
