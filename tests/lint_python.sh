#!/bin/bash
set -e

# Install linting tools if not already installed
if ! command -v black &> /dev/null || ! command -v flake8 &> /dev/null; then
    echo "Installing Python linting tools..."
    pip install black flake8
fi

echo "Running Python code formatting with black..."
black src/ tests/

echo "Running Python code linting with flake8..."
flake8 src/ tests/ --max-line-length=100 --exclude=__pycache__,*.pyc

echo "Python linting completed successfully!" 