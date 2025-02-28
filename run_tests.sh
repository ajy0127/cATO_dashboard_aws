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
python -m pip install pytest boto3

# Run the tests
echo "Running tests..."
cd src
python -m pytest tests/test_lambda_function.py -v

# Check if tests passed
TEST_RESULT=$?
cd ..

# Deactivate virtual environment
deactivate

if [ $TEST_RESULT -eq 0 ]; then
  echo "All tests passed!"
  exit 0
else
  echo "Tests failed!"
  exit 1
fi 