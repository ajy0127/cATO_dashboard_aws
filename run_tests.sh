#!/bin/bash
set -e

echo "=== cATO Dashboard Testing Suite ==="
echo "Running all tests and linting checks..."

# Make scripts executable
chmod +x tests/cfn/test_templates.sh
chmod +x tests/lint_python.sh

# Run CloudFormation linting
echo -e "\n=== CloudFormation Template Linting ==="
./tests/cfn/test_templates.sh

# Run Python linting
echo -e "\n=== Python Code Linting ==="
./tests/lint_python.sh

# Run Python unit tests
echo -e "\n=== Python Unit Tests ==="
python -m unittest discover -s tests/unit

# Ask if integration tests should be run
echo -e "\n=== Integration Tests ==="
read -p "Run integration tests? These will create actual AWS resources. (y/n): " run_integration

if [[ $run_integration == "y" ]]; then
    echo "Running integration tests..."
    python -m unittest discover -s tests/integration
else
    echo "Skipping integration tests."
fi

echo -e "\n=== All tests completed successfully! ===" 