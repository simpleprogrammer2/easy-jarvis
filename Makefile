# Makefile for Jarvis Automation Framework

PYTHON = .venv/bin/python
PIP = .venv/bin/pip
PYTHON_VERSION = 3.12.9

.PHONY: all venv install run lint test clean setup

all: venv install

# Create virtual environment if it doesn't exist
venv:
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		pyenv local $(PYTHON_VERSION); \
		python -m venv .venv; \
	fi

# Install dependencies
install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Run the application
run: venv
	PYTHONPATH=. $(PYTHON) src/main.py

# Lint the project
lint: venv
	.venv/bin/ruff check .

# Run tests
test: venv
	.venv/bin/pytest

# Clean up
clean:
	rm -rf .venv __pycache__ .pytest_cache .ruff_cache

# One-time setup
setup:
	pyenv install $(PYTHON_VERSION) -s
	make all
