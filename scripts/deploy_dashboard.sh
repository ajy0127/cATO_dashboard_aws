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

echo "This script will deploy the cATO Dashboard with Security Hub integration and Athena analysis."
echo "Grafana integration needs to be set up manually after deployment."
echo "For instructions, see docs/grafana-guide.md after deployment completes."

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

echo "Creating deployment package..."
zip -r security_hub_integration.zip lambda_function.py requests/ certifi/ charset_normalizer/ idna/ urllib3/

echo "Uploading Lambda package to S3..."
aws s3 cp security_hub_integration.zip s3://$LAMBDA_BUCKET/ --region $AWS_REGION $PROFILE_PARAM

cd ..

# Deploy with CloudFormation - Simplified deployment only
echo "Deploying CloudFormation stack..."

STACK_NAME="cato-dashboard-$(date +%Y%m%d)"

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
  --template-body file://cloudformation/cato-dashboard-simplified.yaml \
  --parameters \
    ParameterKey=S3BucketName,ParameterValue=$DATA_BUCKET \
    ParameterKey=LambdaCodeBucket,ParameterValue=$LAMBDA_BUCKET \
    ParameterKey=LambdaCodeKey,ParameterValue=security_hub_integration.zip \
    ParameterKey=CreateS3Bucket,ParameterValue=false \
    ParameterKey=LambdaFunctionName,ParameterValue=$LAMBDA_FUNCTION_NAME \
    ParameterKey=AthenaDatabaseName,ParameterValue=$ATHENA_DB_NAME \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $AWS_REGION \
  $PROFILE_PARAM
  
echo "Deployment initiated. Stack name: $STACK_NAME"
echo "Deployment will take approximately 3-5 minutes to complete."

# Instructions for monitoring the deployment
echo ""
echo "To monitor stack creation, run:"
echo "aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].StackStatus' --region $AWS_REGION $PROFILE_PARAM"
echo ""
echo "Once complete, check for Security Hub findings in S3:"
echo "aws s3 ls s3://$DATA_BUCKET/ --region $AWS_REGION $PROFILE_PARAM"
echo ""
echo "To manually invoke the Lambda function:"
echo "aws lambda invoke --function-name $LAMBDA_FUNCTION_NAME --payload '{}' --region $AWS_REGION $PROFILE_PARAM response.json"
echo ""
echo "======= Athena Setup ======="
echo "Athena database and table will be automatically created by the CloudFormation template."
echo "To query your findings in Athena:"
echo "1. Go to the Athena console: https://console.aws.amazon.com/athena/"
echo "2. Select database '$ATHENA_DB_NAME'"
echo "3. Run a query like: SELECT * FROM security_findings LIMIT 10;"
echo ""
echo "======= IMPORTANT: Grafana Setup ======="
echo "To set up Grafana dashboards after deployment:"
echo "1. Ensure you have an Amazon Managed Grafana workspace set up"
echo "2. In Grafana, create a new data source using Athena"
echo "3. Follow the detailed instructions in docs/grafana-guide.md"
echo ""
echo "======= AWS CLI Profile Information ======="
echo "If you don't have an AWS CLI profile set up, create one with:"
echo "aws configure --profile your-profile-name"
echo ""
echo "This will prompt you to enter:"
echo "  - AWS Access Key ID"
echo "  - AWS Secret Access Key"
echo "  - Default region name"
echo "  - Default output format (json recommended)"
echo ""
echo "To list your existing profiles:"
echo "aws configure list-profiles" 