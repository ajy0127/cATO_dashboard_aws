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
python -m pip install pytest boto3 mock cfn-lint
if [ -f "src/requirements.txt" ]; then
  echo "Installing requirements from src/requirements.txt..."
  python -m pip install -r src/requirements.txt
fi

# Set required environment variables for tests
export S3_BUCKET_NAME="test-bucket"
export ATHENA_RESULTS_BUCKET="test-athena-bucket"

# Run CloudFormation linting
echo "Running CloudFormation linting..."
echo "=================================="
cfn-lint cloudformation/*.yaml
CFN_LINT_RESULT=$?

if [ $CFN_LINT_RESULT -ne 0 ]; then
  echo "CloudFormation linting failed! Please fix the issues before proceeding."
  deactivate
  exit 1
fi

# Run the tests
echo "Running Lambda function tests..."
echo "================================"
# Run tests from the root directory
python -m pytest tests/test_lambda_function.py tests/test_custom_resource.py -v

# Check if tests passed
TEST_RESULT=$?

# Deactivate virtual environment
deactivate

if [ $TEST_RESULT -eq 0 ]; then
  echo "All tests passed!"
  exit 0
else
  echo "Tests failed!"
  exit 1
fi 