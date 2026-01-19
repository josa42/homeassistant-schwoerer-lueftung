.PHONY: help venv install test lint clean dev-up dev-down dev-logs dev-restart

PYTHON := $(shell command -v python3 || command -v python)
VENV := venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip

help:
	@echo "Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make dev-up       - Start local Home Assistant for testing"
	@echo "  make dev-down     - Stop local Home Assistant"
	@echo "  make dev-logs     - Follow Home Assistant logs"
	@echo "  make dev-restart  - Restart after code changes"
	@echo ""
	@echo "Testing:"
	@echo "  make venv     - Create virtual environment"
	@echo "  make install  - Install test dependencies (creates venv if needed)"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linter"
	@echo "  make clean    - Clean cache files"

venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV); \
		echo "Virtual environment created at ./$(VENV)"; \
		echo "To activate: source $(VENV_BIN)/activate"; \
	else \
		echo "Virtual environment already exists"; \
	fi

install: venv
	@echo "Installing dependencies in virtual environment..."
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements_test.txt
	$(VENV_PIP) install ruff
	@echo "Done! Activate with: source $(VENV_BIN)/activate"

test:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	$(VENV_PYTHON) -m pytest tests/ -v

lint:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	$(VENV_BIN)/ruff check custom_components/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf $(VENV)

dev-up:
	@echo "Starting Home Assistant..."
	@echo "Access at: http://localhost:8123"
	docker-compose up -d
	@echo ""
	@echo "Waiting for Home Assistant to start..."
	@sleep 5
	docker-compose logs -f --tail=50

dev-down:
	docker-compose down

dev-logs:
	docker-compose logs -f

dev-restart:
	@echo "Restarting Home Assistant..."
	docker-compose restart
	@sleep 2
	docker-compose logs -f --tail=50
