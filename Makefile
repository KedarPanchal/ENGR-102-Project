VENV := venv/bin/activate

.PHONY: help all build run clean ui

help:
	@echo "Available targets:"
	@echo "  help        - Show this help message"
	@echo "  all         - Clean, build, and run the project"
	@echo "  build       - Build the project"
	@echo "  run         - Run the project"
	@echo "  clean       - Clean build artifacts"
	@echo "  ui          - Run UI tests"

all: clean build run

build: $(VENV)

$(VENV):
	@echo "Creating virtual environment..."
	python3 -m venv venv
	. $(VENV)
	@echo "Upgrading pip..."
	python3 -m pip install --upgrade pip
	@echo "Installing dependencies..."
	python3 -m pip install -r requirements.txt

run:
	@echo "Entering virtual environment..."
	. $(VENV)
	@echo "Running the project..."
	python3 main.py

clean:
	@echo "Removing virtual environment..."
	rm -rf venv
	@echo "Removing build artifacts..."
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +

ui:
	@echo "Entering virtual environment..."
	. $(VENV)
	@echo "Running UI tests..."
	python3 -m tui.ui
