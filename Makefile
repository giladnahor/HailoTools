# Hailo Utils - Makefile for easy installation and development

.PHONY: help install install-dev install-deps clean test lint format check build docs

# Default target
help:
	@echo "Hailo Utils - Available targets:"
	@echo ""
	@echo "Installation:"
	@echo "  install-deps    Install system dependencies (Ubuntu/Debian)"
	@echo "  install         Install the package"
	@echo "  install-dev     Install in development mode with dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test           Run tests"
	@echo "  lint           Run linting (flake8, mypy)"
	@echo "  format         Format code (black, isort)"
	@echo "  check          Run all checks (lint + test)"
	@echo ""
	@echo "Build & Distribution:"
	@echo "  build          Build distribution packages"
	@echo "  clean          Clean build artifacts"
	@echo ""
	@echo "Documentation:"
	@echo "  docs           Build documentation"

# Installation targets
install-deps:
	@echo "Installing system dependencies..."
	sudo apt-get update
	sudo apt-get install -y python3 python3-pip python3-venv pkg-config
	sudo apt-get install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
	sudo apt-get install -y gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-plugins-bad
	sudo apt-get install -y libgstrtspserver-1.0-dev
	sudo apt-get install -y libgirepository1.0-dev
	@echo "System dependencies installed successfully!"

install:
	pip install .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Development targets
test:
	pytest tests/ -v --cov=hailo_utils --cov-report=term-missing

test-fast:
	pytest tests/ -v -x -m "not slow"

lint:
	flake8 hailo_utils/ tests/
	mypy hailo_utils/

format:
	black hailo_utils/ tests/
	isort hailo_utils/ tests/

format-check:
	black --check hailo_utils/ tests/
	isort --check-only hailo_utils/ tests/

check: format-check lint test

# Build targets
build:
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Documentation
docs:
	cd docs && make html

docs-clean:
	cd docs && make clean

# Docker targets
docker-build:
	docker build -t hailo-utils .

docker-run:
	docker run --rm -it --privileged -v /dev:/dev hailo-utils

# Environment setup
setup-env:
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "source venv/bin/activate"

# Release targets
release-test:
	python -m build
	python -m twine check dist/*
	python -m twine upload --repository testpypi dist/*

release:
	python -m build
	python -m twine check dist/*
	python -m twine upload dist/*

# Utility targets
show-deps:
	@echo "System dependencies:"
	@echo "  - Python 3.8+"
	@echo "  - GStreamer 1.0"
	@echo "  - pkg-config"
	@echo ""
	@echo "Optional dependencies:"
	@echo "  - Hailo TAPPAS (for AI features)"
	@echo "  - PyGObject (for GStreamer integration)"

check-system:
	@echo "Checking system requirements..."
	@python3 --version || echo "❌ Python 3 not found"
	@pkg-config --version || echo "❌ pkg-config not found"
	@pkg-config --exists gstreamer-1.0 && echo "✅ GStreamer found" || echo "❌ GStreamer not found"
	@pkg-config --exists gstreamer-rtsp-server-1.0 && echo "✅ GStreamer RTSP Server found" || echo "❌ GStreamer RTSP Server not found"
	@python3 -c "import gi; print('✅ PyGObject available')" 2>/dev/null || echo "❌ PyGObject not available"