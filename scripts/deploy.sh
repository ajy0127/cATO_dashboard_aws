#!/bin/bash
set -e

# Wrapper script for cATO Dashboard deployment
echo "=========================================="
echo "cATO Dashboard Deployment"
echo "=========================================="

# Check if we're running in a CI/CD environment
if [ -n "$CI" ]; then
  echo "Running in CI/CD environment"
  
  # Set default values for CI/CD deployment
  export AWS_REGION=${AWS_REGION:-"us-east-1"}
  export STACK_NAME=${STACK_NAME:-"cato-dashboard-ci"}
  
  # In a real CI/CD pipeline, you would use GitHub secrets or environment variables
  # to configure the deployment parameters
  
  echo "Using AWS region: $AWS_REGION"
  echo "Using stack name: $STACK_NAME"
  
  # For CI/CD, we'll just echo success since we don't want to actually deploy
  # resources in the GitHub Actions environment without proper credentials
  echo "CI/CD deployment simulation completed successfully"
  echo "In a real deployment, this would deploy the cATO Dashboard stack"
  exit 0
else
  # For local development, call the actual deployment script
  echo "Running deployment script locally"
  
  # Call the main deployment script
  ./scripts/deploy_dashboard.sh
fi 