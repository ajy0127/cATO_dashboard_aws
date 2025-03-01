#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "Installing required packages..."
python -m pip install cfn-lint

# Run CloudFormation linting
echo "Running CloudFormation linting..."
echo "=================================="

# Check all CloudFormation templates
cfn-lint cloudformation/*.yaml

# Store the exit code
LINT_RESULT=$?

# Deactivate virtual environment
deactivate

# Return the appropriate exit code
if [ $LINT_RESULT -eq 0 ]; then
  echo "All CloudFormation templates passed linting!"
  exit 0
else
  echo "CloudFormation linting found issues that need to be fixed."
  exit 1
fi 