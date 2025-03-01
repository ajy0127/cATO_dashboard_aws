# Deployment Guide for cATO Dashboard

This guide provides step-by-step instructions for deploying the cATO Dashboard with Security Hub integration. The Grafana dashboard setup is handled as a separate manual process after deployment (see the Grafana Integration Guide for details).

## Prerequisites

Before you begin, make sure you have the following:

1. **AWS Account** with permissions to create IAM roles, Lambda functions, S3 buckets, Athena resources, and EventBridge rules
2. **AWS Security Hub** enabled with NIST 800-53 standard activated
3. **AWS CLI** installed and configured with appropriate access credentials
4. **Amazon Managed Grafana** workspace (only if you plan to set up the Grafana dashboard after deployment)
5. **Python 3.8+** installed (for local testing and development)

### Setting Up AWS CLI Profiles (Optional)

AWS CLI profiles allow you to manage multiple sets of AWS credentials, which is useful if you need to deploy to different AWS accounts or regions.

To create a new AWS CLI profile:

```bash
aws configure --profile your-profile-name
```

You'll be prompted to enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (e.g., us-east-1)
- Default output format (json recommended)

To list your existing profiles:

```bash
aws configure list-profiles
```

## Deployment Process

The deployment script will guide you through setting up the Security Hub integration component of the cATO Dashboard.

### Clone the Repository

```bash
git clone https://github.com/yourusername/cato-dashboard.git
cd cato-dashboard
```

### Run the Deployment Script

Make the deployment script executable:

```bash
chmod +x scripts/deploy_dashboard.sh
./scripts/deploy_dashboard.sh
```

The script will:
1. Create an S3 bucket for Lambda code
2. Create an S3 bucket for Security Hub findings data
3. Package and upload the Lambda function
4. Deploy the CloudFormation stack
5. Set up initial data collection

### Manual Deployment (Alternative)

If you prefer to deploy manually or need more control over the process, follow these steps:

#### 1. Create S3 Buckets

Create two S3 buckets:
- One for Lambda code
- One for Security Hub findings data

```bash
aws s3 mb s3://your-lambda-code-bucket --region your-region
aws s3 mb s3://your-findings-data-bucket --region your-region
```

#### 2. Package and Upload Lambda Code

```bash
cd src
zip -r ../lambda_function.zip lambda_function.py
cd ..
aws s3 cp lambda_function.zip s3://your-lambda-code-bucket/
```

#### 3. Deploy CloudFormation Stack

```bash
aws cloudformation deploy \
  --template-file cloudformation/cato-dashboard.yaml \
  --stack-name cato-dashboard \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    S3BucketName=your-findings-data-bucket \
    LambdaCodeBucket=your-lambda-code-bucket \
    LambdaCodeKey=lambda_function.zip \
    CreateS3Bucket=false \
    CreateAthenaResultsBucket=true \
    LambdaFunctionName=cato-security-hub-integration \
    AthenaDatabaseName=cato_security_findings \
    GrafanaIntegration=false
```

## Testing the Deployment

To verify that the deployment was successful:

1. Check that the Lambda function is running correctly:
```bash
aws lambda invoke --function-name cato-security-hub-integration --payload '{}' response.json
cat response.json
```

2. Check that data is being collected in the S3 bucket:
```bash
aws s3 ls s3://your-findings-data-bucket/ --recursive
```

3. Run the automated tests:
```bash
./scripts/run_tests.sh
```

### Check Deployment Status

Monitor the CloudFormation stack creation:

```bash
aws cloudformation describe-stacks \
  --stack-name cato-dashboard-YYYYMMDD \
  --profile <your-profile-name> \
  --query 'Stacks[0].StackStatus'
```

The deployment is complete when the status is `CREATE_COMPLETE`.

### Verify Deployment

Verify that the deployment was successful by checking the following:

1. Check if the S3 bucket was created and contains data:

```bash
aws s3 ls s3://cato-dashboard-data-<timestamp>-<random>/ --profile <your-profile-name>
```

2. Test the Lambda function by invoking it (use the unique Lambda function name shown during deployment):

```bash
aws lambda invoke \
  --function-name cato-security-hub-integration-<timestamp>-<random> \
  --profile <your-profile-name> \
  --payload '{}' \
  response.json
```

3. Check CloudWatch Logs for the Lambda function:

```bash
aws logs get-log-events \
  --log-group-name /aws/lambda/cato-security-hub-integration-<timestamp>-<random> \
  --profile <your-profile-name> \
  --log-stream-name $(aws logs describe-log-streams \
    --log-group-name /aws/lambda/cato-security-hub-integration-<timestamp>-<random> \
    --profile <your-profile-name> \
    --query 'logStreams[0].logStreamName' \
    --output text)
```

## Setting Up Grafana After Deployment

For detailed instructions on manually setting up the Grafana dashboard using data from your deployed solution, refer to the [Grafana Integration Guide](grafana-guide.md).

The guide covers:
- Creating a Grafana workspace
- Setting up Athena as a data source
- Creating visualizations for compliance metrics
- Adding annotations for finding updates
- Sharing your dashboard with team members

## Using the Full Deployment Script

If you prefer a more automated approach, you can use the provided deployment script:

```bash
./deploy.sh
```

This script will:
1. Create unique S3 bucket names
2. Build and upload the Lambda package
3. Deploy the CloudFormation stack
4. Monitor the deployment until it completes
5. Display instructions for next steps

After deployment:
1. Check the S3 bucket for collected findings
2. Follow the [Grafana Integration Guide](grafana-guide.md) to set up your visualization dashboard
3. Customize your Grafana dashboard as needed for your organization

## Troubleshooting

### Common Issues

1. **CloudFormation Stack Creation Fails**
   - Check the CloudFormation Events tab in the AWS Console
   - Common causes: S3 bucket name conflicts, insufficient permissions, hitting service limits
   - Solution: Review error messages and make necessary adjustments

2. **Resource Already Exists Error**
   - Error: "Resource already exists in another stack" during deployment
   - Cause: You've previously deployed the stack with the same resource names
   - Solution: The current script generates unique resource names to avoid this issue. If you're using an older version of the script, update to the latest version or delete the conflicting stack before deployment.

3. **Missing Dependencies**
   - Error: Lambda functions fail with import errors
   - Solution: Make sure the Lambda package includes all required dependencies

4. **S3 Bucket Name Conflicts**
   - Error: "Bucket already exists" during deployment
   - Solution: Try a different unique identifier when running the deployment script

5. **Security Hub Integration Issues**
   - Error: No findings are being processed
   - Solution: 
     - Ensure Security Hub is enabled with the NIST 800-53 standard
     - Check EventBridge rule is properly configured
     - Verify Lambda function has necessary permissions

6. **AWS Profile Authentication Errors**
   - Error: "Unable to locate credentials" or "Access Denied"
   - Solution:
     - Verify profile exists: `aws configure list-profiles`
     - Validate credentials: `aws sts get-caller-identity --profile <your-profile-name>`
     - Ensure the user has sufficient permissions

### Viewing Lambda Logs

To view CloudWatch logs for troubleshooting Lambda issues:

```bash
aws logs get-log-events \
  --log-group-name /aws/lambda/cato-security-hub-integration-<timestamp>-<random> \
  --profile <your-profile-name> \
  --log-stream-name $(aws logs describe-log-streams \
    --log-group-name /aws/lambda/cato-security-hub-integration-<timestamp>-<random> \
    --profile <your-profile-name> \
    --order-by LastEventTime \
    --descending \
    --limit 1 \
    --query 'logStreams[0].logStreamName' \
    --output text)
```

### Cleaning Up Resources

If you need to delete the deployment:

```bash
aws cloudformation delete-stack \
  --stack-name cato-dashboard-YYYYMMDD \
  --profile <your-profile-name>
```

## Next Steps

After successful deployment:

1. Verify that Security Hub findings are being processed correctly
2. Follow the [Grafana Integration Guide](grafana-guide.md) to set up your visualization dashboard
3. Customize your Grafana dashboard as needed for your organization

## Getting Help

If you encounter issues not covered in this guide, please:
1. Check the project's GitHub Issues section
2. Review AWS service quotas and limits
3. Contact project maintainers for support 