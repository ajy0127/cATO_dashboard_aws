#!/bin/bash
set -e

# cATO Dashboard Deployment Script
echo "=========================================="
echo "cATO Dashboard Deployment Script"
echo "=========================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
  echo "Error: AWS CLI is not installed. Please install it first."
  exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
  echo "Error: Python 3 is not installed. Please install it first."
  exit 1
fi

# Prompt for AWS profile
read -p "Enter AWS CLI profile to use (leave blank for default): " AWS_PROFILE
PROFILE_PARAM=""
if [ -n "$AWS_PROFILE" ]; then
  PROFILE_PARAM="--profile $AWS_PROFILE"
  echo "Using AWS profile: $AWS_PROFILE"
else
  echo "Using default AWS profile"
fi

# Prompt for AWS region
read -p "Enter AWS region (e.g., us-east-1): " AWS_REGION
if [ -z "$AWS_REGION" ]; then
  echo "Error: AWS region is required."
  exit 1
fi

# Prompt for Grafana authentication details
read -p "Enter Grafana admin username [admin]: " ADMIN_USERNAME
ADMIN_USERNAME=${ADMIN_USERNAME:-"admin"}

read -s -p "Enter Grafana admin password (min 8 characters): " ADMIN_PASSWORD
echo
if [ ${#ADMIN_PASSWORD} -lt 8 ]; then
  echo "Error: Admin password must be at least 8 characters long."
  exit 1
fi

read -p "Enter Grafana viewer username [viewer]: " VIEWER_USERNAME
VIEWER_USERNAME=${VIEWER_USERNAME:-"viewer"}

read -s -p "Enter Grafana viewer password (min 8 characters): " VIEWER_PASSWORD
echo
if [ ${#VIEWER_PASSWORD} -lt 8 ]; then
  echo "Error: Viewer password must be at least 8 characters long."
  exit 1
fi

echo "This script will deploy the cATO Dashboard with Security Hub integration, Athena analysis, and self-hosted Grafana visualization."

# Generate unique names with timestamp and random suffix
TIMESTAMP=$(date +%Y%m%d%H%M%S)
RANDOM_SUFFIX=$(openssl rand -hex 4)
LAMBDA_BUCKET="cato-lambda-code-${TIMESTAMP}-${RANDOM_SUFFIX}"
DATA_BUCKET="cato-dashboard-data-${TIMESTAMP}-${RANDOM_SUFFIX}"
ATHENA_RESULTS_BUCKET="${DATA_BUCKET}-athena-results"
LAMBDA_FUNCTION_NAME="cato-security-hub-integration-${TIMESTAMP}-${RANDOM_SUFFIX}"
ATHENA_DB_NAME="cato_security_findings_${TIMESTAMP}"

echo "Creating S3 buckets:"
echo "- Lambda code bucket: $LAMBDA_BUCKET"
echo "- Data bucket: $DATA_BUCKET"
echo "- Athena results bucket: $ATHENA_RESULTS_BUCKET"
echo "- Lambda function name: $LAMBDA_FUNCTION_NAME"
echo "- Athena database name: $ATHENA_DB_NAME"

# Create S3 buckets
aws s3 mb s3://$LAMBDA_BUCKET --region $AWS_REGION $PROFILE_PARAM
aws s3 mb s3://$DATA_BUCKET --region $AWS_REGION $PROFILE_PARAM

echo "S3 buckets created successfully."

# Build and upload Lambda package
echo "Building Lambda package..."
cd src || exit 1

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
  echo "Installing dependencies..."
  python3 -m pip install -r requirements.txt -t .
else
  echo "No requirements.txt found. Installing required packages..."
  python3 -m pip install requests boto3 -t .
fi

# Install Grafana client for annotations
echo "Installing Grafana client..."
python3 -m pip install grafana-client -t .

echo "Creating deployment package..."
zip -r security_hub_integration.zip lambda_function.py requests/ certifi/ charset_normalizer/ idna/ urllib3/ grafana_client/

echo "Uploading Lambda package to S3..."
aws s3 cp security_hub_integration.zip s3://$LAMBDA_BUCKET/ --region $AWS_REGION $PROFILE_PARAM

cd ..

# Deploy with CloudFormation
echo "Deploying CloudFormation stack..."

STACK_NAME="cato-dashboard"

# Check if stack already exists and delete it if it's in a failed state
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION $PROFILE_PARAM --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "STACK_NOT_FOUND")

if [ "$STACK_STATUS" != "STACK_NOT_FOUND" ]; then
  if [[ "$STACK_STATUS" == *ROLLBACK* || "$STACK_STATUS" == *FAILED* ]]; then
    echo "Stack $STACK_NAME exists in $STACK_STATUS state. Deleting it before creating a new one..."
    aws cloudformation delete-stack --stack-name $STACK_NAME --region $AWS_REGION $PROFILE_PARAM
    echo "Waiting for stack deletion to complete..."
    aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $AWS_REGION $PROFILE_PARAM
    echo "Stack deletion complete."
  else
    echo "Stack $STACK_NAME exists in $STACK_STATUS state."
    read -p "Do you want to replace this stack? (y/n): " REPLACE_STACK
    if [[ "$REPLACE_STACK" == "y" || "$REPLACE_STACK" == "Y" ]]; then
      echo "Deleting existing stack..."
      aws cloudformation delete-stack --stack-name $STACK_NAME --region $AWS_REGION $PROFILE_PARAM
      echo "Waiting for stack deletion to complete..."
      aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $AWS_REGION $PROFILE_PARAM
      echo "Stack deletion complete."
    else
      echo "Deployment cancelled. Exiting."
      exit 0
    fi
  fi
fi

echo "Creating new CloudFormation stack: $STACK_NAME"
aws cloudformation create-stack \
  --stack-name $STACK_NAME \
  --template-body file://cloudformation/grafana-cato-dashboard.yaml \
  --parameters \
    ParameterKey=AdminUsername,ParameterValue=$ADMIN_USERNAME \
    ParameterKey=AdminPassword,ParameterValue=$ADMIN_PASSWORD \
    ParameterKey=ViewerUsername,ParameterValue=$VIEWER_USERNAME \
    ParameterKey=ViewerPassword,ParameterValue=$VIEWER_PASSWORD \
    ParameterKey=InstanceType,ParameterValue=t3.small \
    ParameterKey=AdminIpRange,ParameterValue=0.0.0.0/0 \
    ParameterKey=EnableHttps,ParameterValue=true \
    ParameterKey=AthenaDatabase,ParameterValue=$ATHENA_DB_NAME \
    ParameterKey=AthenaTable,ParameterValue=security_findings \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $AWS_REGION \
  $PROFILE_PARAM
  
echo "Deployment initiated. Stack name: $STACK_NAME"
echo "Deployment will take approximately 3-5 minutes to complete."

# Wait for stack creation to complete
echo "Waiting for stack creation to complete..."
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $AWS_REGION $PROFILE_PARAM || {
  echo "Stack creation failed or timed out. Check the AWS CloudFormation console for details."
  exit 1
}

echo "Stack creation completed successfully!"

# Get Grafana access URL and display credentials
GRAFANA_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION $PROFILE_PARAM --query 'Stacks[0].Outputs[?OutputKey==`GrafanaURL`].OutputValue' --output text)

echo ""
echo "=========================================="
echo "Access Your Grafana Dashboard"
echo "=========================================="
echo "Grafana URL: $GRAFANA_URL"
echo ""
echo "Admin credentials:"
echo "Username: $ADMIN_USERNAME"
echo "Password: (the one you entered during deployment)"
echo ""
echo "Viewer credentials:"
echo "Username: $VIEWER_USERNAME"
echo "Password: (the one you entered during deployment)"
echo ""
echo "Note: It may take a few minutes for the EC2 instance to fully initialize."
echo "If you cannot access Grafana immediately, please wait a few minutes and try again."
echo ""
echo "Security Hub findings will be collected and stored in S3:"
echo "s3://$DATA_BUCKET/"
echo ""
echo "For complete instructions on using your dashboard, refer to:"
echo "docs/grafana-guide.md"
echo ""
echo "==========================================" 