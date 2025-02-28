# cATO Dashboard Deployment Guide

This guide provides step-by-step instructions for deploying the cATO Dashboard solution with AWS CloudFormation. It includes both the simplified deployment (Security Hub integration only) and the full deployment with QuickSight integration.

## Prerequisites

Before starting deployment, ensure you have:

1. An AWS account with administrator access
2. AWS CLI installed and configured with appropriate credentials
3. Security Hub enabled in your AWS account with NIST 800-53 standard
4. (For full deployment) QuickSight Enterprise Edition subscription
5. Python 3.9 or higher installed on your local machine

## Simplified Deployment (Security Hub Integration Only)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/cato-dashboard.git
cd cato-dashboard
```

### Step 2: Create S3 Buckets

```bash
# Create unique bucket names
export LAMBDA_BUCKET="cato-lambda-code-$(date +%Y%m%d%H%M%S)-$(openssl rand -hex 4)"
export DATA_BUCKET="cato-dashboard-data-$(date +%Y%m%d%H%M%S)-$(openssl rand -hex 4)"

# Create the buckets
aws s3 mb s3://$LAMBDA_BUCKET --region <your-region>
aws s3 mb s3://$DATA_BUCKET --region <your-region>
```

### Step 3: Build and Upload Lambda Package

```bash
# Install dependencies and create zip package
cd src
python3 -m pip install -r requirements.txt -t .
zip -r security_hub_integration.zip lambda_function.py requests/ certifi/ charset_normalizer/ idna/ urllib3/
aws s3 cp security_hub_integration.zip s3://$LAMBDA_BUCKET/ --region <your-region>
cd ..
```

### Step 4: Deploy with CloudFormation

```bash
aws cloudformation create-stack \
  --stack-name cato-dashboard \
  --template-body file://cloudformation/cato-dashboard-simplified.yaml \
  --parameters \
    ParameterKey=S3BucketName,ParameterValue=$DATA_BUCKET \
    ParameterKey=LambdaCodeBucket,ParameterValue=$LAMBDA_BUCKET \
    ParameterKey=LambdaCodeKey,ParameterValue=security_hub_integration.zip \
    ParameterKey=CreateS3Bucket,ParameterValue=false \
  --capabilities CAPABILITY_NAMED_IAM \
  --region <your-region>
```

### Step 5: Monitor the Deployment

```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name cato-dashboard \
  --query 'Stacks[0].StackStatus' \
  --region <your-region>
```

The deployment should complete in 3-5 minutes. You can also monitor the progress in the AWS CloudFormation console.

### Step 6: Verify the Deployment

Once the stack creation is complete, verify that:

1. The Lambda function has been created and works properly
2. Security Hub findings are being stored in the S3 bucket
3. The EventBridge rule is configured to trigger the Lambda

```bash
# Check if files exist in S3
aws s3 ls s3://$DATA_BUCKET/ --region <your-region>

# Test the Lambda function manually
aws lambda invoke \
  --function-name cato-security-hub-integration \
  --payload '{}' \
  --region <your-region> \
  response.json

# Check the Lambda output
cat response.json
```

## Full Deployment with QuickSight Integration

### Step Modifications for Full Deployment

Follow the same steps 1-3 as in the simplified deployment, then:

### Step 4 (Modified): Deploy with Full CloudFormation Template

```bash
# Create a QuickSight admin user if you don't have one
export QUICKSIGHT_USER_EMAIL="your-email@example.com"

aws cloudformation create-stack \
  --stack-name cato-dashboard-full \
  --template-body file://cloudformation/cato-dashboard-setup.yaml \
  --parameters \
    ParameterKey=S3BucketName,ParameterValue=$DATA_BUCKET \
    ParameterKey=LambdaCodeBucket,ParameterValue=$LAMBDA_BUCKET \
    ParameterKey=LambdaCodeKey,ParameterValue=security_hub_integration.zip \
    ParameterKey=QuickSightUserEmail,ParameterValue=$QUICKSIGHT_USER_EMAIL \
    ParameterKey=DashboardRefreshRate,ParameterValue=24 \
    ParameterKey=WaitTimeForDashboardCreation,ParameterValue=180 \
  --capabilities CAPABILITY_NAMED_IAM \
  --region <your-region> \
  --timeout-in-minutes 30
```

### Step 5 (Modified): Monitor the Full Deployment

```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name cato-dashboard-full \
  --query 'Stacks[0].StackStatus' \
  --region <your-region>
```

The full deployment can take 15-20 minutes due to the QuickSight setup.

### Step 6 (Modified): Access the QuickSight Dashboard

1. Sign in to QuickSight with the admin email provided
2. Navigate to the Dashboards section
3. Open the "cATO Dashboard" 
4. The dashboard should display your Security Hub findings and compliance status

## Troubleshooting

### Common Issues and Solutions

1. **CloudFormation Stack Creation Stalling**:
   - Check the Lambda function logs in CloudWatch for errors
   - Verify Security Hub is properly configured
   - Try the simplified deployment first before attempting the full deployment

2. **Missing Dependencies in Lambda Package**:
   - Ensure you've installed all dependencies correctly with `pip install -r requirements.txt -t .`
   - Verify that all necessary directories are included in the zip file

3. **S3 Bucket Already Exists**:
   - S3 bucket names must be globally unique
   - If you get an error that the bucket already exists, generate a new bucket name

4. **QuickSight Access Issues**:
   - Ensure your QuickSight subscription is active
   - Verify the email used is registered with QuickSight
   - Check IAM permissions for QuickSight access

### Viewing CloudWatch Logs

To check the Lambda function logs for errors:

```bash
# Get the log group name
LOG_GROUP_NAME="/aws/lambda/cato-security-hub-integration"

# Get the most recent log stream
LOG_STREAM=$(aws logs describe-log-streams \
  --log-group-name $LOG_GROUP_NAME \
  --order-by LastEventTime \
  --descending \
  --limit 1 \
  --query 'logStreams[0].logStreamName' \
  --output text \
  --region <your-region>)

# View the logs
aws logs get-log-events \
  --log-group-name $LOG_GROUP_NAME \
  --log-stream-name $LOG_STREAM \
  --region <your-region>
```

## Cleaning Up Resources

If you need to remove the deployed resources:

```bash
# Delete the CloudFormation stack
aws cloudformation delete-stack \
  --stack-name cato-dashboard \
  --region <your-region>

# Delete the S3 buckets
aws s3 rm s3://$DATA_BUCKET --recursive --region <your-region>
aws s3 rb s3://$DATA_BUCKET --region <your-region>

aws s3 rm s3://$LAMBDA_BUCKET --recursive --region <your-region>
aws s3 rb s3://$LAMBDA_BUCKET --region <your-region>
```

## Next Steps

After successful deployment:

1. Verify that Security Hub findings are being updated correctly
2. Customize the QuickSight dashboard for your specific requirements
3. Set up alerts for critical findings
4. Schedule regular reviews of the compliance status

For more information on using the QuickSight dashboard, refer to the [QuickSight Guide](quicksight-guide.md). 