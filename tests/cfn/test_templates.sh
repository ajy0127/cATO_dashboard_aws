#!/bin/bash
set -e

# Install cfn-lint if not already installed
if ! command -v cfn-lint &> /dev/null; then
    echo "Installing cfn-lint..."
    pip install cfn-lint
fi

echo "Running CloudFormation linting..."

# Test the main CloudFormation template
cfn-lint cloudformation/cato-dashboard.yaml

# Test the Grafana CloudFormation template
cfn-lint cloudformation/grafana-cato-dashboard.yaml

echo "CloudFormation linting completed successfully!" 