#!/bin/bash

# Run tests first
echo "Running tests before deployment..."
./scripts/run_tests.sh

# Check if tests passed
if [ $? -ne 0 ]; then
  echo "Tests failed! Aborting deployment."
  exit 1
fi

# Configure Git
echo "Configuring Git..."
git config --global user.name "${GIT_USERNAME:-GitHub Actions}"
git config --global user.email "${GIT_EMAIL:-actions@github.com}"

# Add remote repository if it doesn't exist
if ! git remote | grep -q "target"; then
  echo "Adding target remote repository..."
  git remote add target https://github.com/ajy0127/cATO_dashboard_aws.git
fi

# Push to target repository
echo "Pushing to target repository..."
git push target HEAD:main --force

echo "Deployment completed successfully!" 