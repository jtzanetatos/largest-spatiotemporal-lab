# justfile

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
# Use bash and strict mode (commands fail immediately on error)
set shell := ["bash", "-uc"]

# Load .env file automatically if it exists (great for API keys)
set dotenv-load

# -----------------------------------------------------------------------------
# UV Commands
# -----------------------------------------------------------------------------

# Lock dependencies
lock:
    uv lock

# -----------------------------------------------------------------------------
# Recipes
# -----------------------------------------------------------------------------

# List available commands
default:
    @just --list

# -----------------------------------------------------------------------------
# Setup & Maintenance
# -----------------------------------------------------------------------------

# Install dependencies, pull data, and setup hooks
# Install dependencies, pull data, and setup hooks
setup:
    @echo "Installing python dependencies..."
    # uv sync creates the venv and installs deps (including editable install of project)
    uv sync
    @echo "Pulling data from DVC..."
    dvc pull
    @echo "Installing pre-commit hooks..."
    pre-commit install
    @echo "Configuring notebook filters..."
    sh tools/setup_notebooks.sh
    @echo "Setup complete! Ready to train."

# Update dependencies from pyproject.toml
update:
    uv lock --upgrade
    uv sync

# Clean up cache, build artifacts, and pycache
clean:
    rm -rf dist/ build/ .pytest_cache/ .mypy_cache/
    find . -type d -name "__pycache__" -exec rm -rf {} +
    @echo "Cleaned up."

# -----------------------------------------------------------------------------
# Quality Control
# -----------------------------------------------------------------------------

# Run all checks (lint + format + test)
check: lint format test

# Run ruff linter
lint:
    ruff check src tests

# Run code formatting
format:
    ruff format src tests

# Run static type checking
type-check:
    mypy src

# Run tests
test:
    pytest tests/

# -----------------------------------------------------------------------------
# MLOps & Training
# -----------------------------------------------------------------------------

# Run training. Usage: just train experiment=baseline model.lr=0.01
# The '+' allows passing arbitrary arguments to hydra
train +hydra_args:
    python -m spatiotemporal_lab.cli.train {{ hydra_args }}

# Run a hyperparameter sweep (Optuna)
sweep:
    python -m spatiotemporal_lab.cli.train -m hydra/sweeper=optuna

# Start the MLFlow UI
mlflow:
    mlflow ui