#!/bin/bash
# Script to build and package the Lambda function

set -e

# Configuration
LAMBDA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${LAMBDA_DIR}/dist"
PACKAGE_NAME="security_hub_integration.zip"

# Create output directory if it doesn't exist
mkdir -p "${OUTPUT_DIR}"

# Clean any previous build
rm -f "${OUTPUT_DIR}/${PACKAGE_NAME}"

echo "Installing dependencies..."
# Create temporary directory for dependencies
TEMP_DIR=$(mktemp -d)
python3 -m pip install --target "${TEMP_DIR}" boto3

echo "Building package..."
# Create zip file with Lambda code
cd "${TEMP_DIR}"
zip -r "${OUTPUT_DIR}/${PACKAGE_NAME}" .

# Add Lambda function code to the zip
cd "${LAMBDA_DIR}"
zip -g "${OUTPUT_DIR}/${PACKAGE_NAME}" security_hub_integration.py

echo "Package created at: ${OUTPUT_DIR}/${PACKAGE_NAME}"
echo "Upload this package to your S3 bucket for CloudFormation deployment."

# Clean up
rm -rf "${TEMP_DIR}" 