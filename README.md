# cATO Dashboard Project

This project provides infrastructure-as-code and documentation for setting up a continuous Authority to Operate (cATO) dashboard using AWS QuickSight with automated data integration from AWS Security Hub. The dashboard helps Information System Security Officers (ISSOs) and Authorizing Officials (AOs) monitor NIST 800-53 compliance in real-time.

## Project Structure

```
.
├── README.md                              # This file
├── cloudformation/
│   ├── cato-dashboard-setup.yaml          # Full CloudFormation template with QuickSight integration
│   └── cato-dashboard-simplified.yaml     # Simplified template for Security Hub integration only
├── docs/
│   └── quicksight-guide.md                # Guide for using the QuickSight dashboard
└── src/
    ├── lambda_function.py                 # Lambda function for Security Hub integration
    └── requirements.txt                   # Python dependencies for the Lambda function
```

## Overview

This solution automatically creates a comprehensive cATO dashboard by:

1. Deploying a Lambda function that pulls compliance data from AWS Security Hub
2. Transforming the data into a dashboard-friendly format and storing it in S3
3. Setting up automated updates via EventBridge when Security Hub findings change
4. Optionally integrating with QuickSight for visualization (full template only)

## Recent Updates

The codebase has been improved with the following changes:

1. **Enhanced CloudFormation Support**: The Lambda function now properly handles CloudFormation custom resource requests, ensuring smoother and more reliable deployments.

2. **Conditional S3 Bucket Creation**: The CloudFormation template now includes a parameter to decide whether to create a new S3 bucket or use an existing one.

3. **Improved Error Handling**: The Lambda function has better error handling and logging to help troubleshoot issues.

4. **Fixed Deployment Issues**: Addressed issues that could cause the CloudFormation stack to stall during deployment.

## Prerequisites

- AWS Account with the following services enabled:
  - AWS Security Hub with NIST 800-53 standard enabled
  - AWS Lambda and CloudFormation
  - Amazon QuickSight Enterprise Edition (for full dashboard setup only)
- IAM permissions to create roles, Lambda functions, and S3 buckets
- AWS CLI configured with appropriate credentials

## Quick Start

### Option 1: Simplified Deployment (Security Hub Integration Only)

This option sets up the automated data collection from Security Hub without QuickSight integration.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/cato-dashboard.git
cd cato-dashboard
```

#### Step 2: Create S3 Buckets

```bash
# Create unique bucket names
export LAMBDA_BUCKET="cato-lambda-code-$(date +%Y%m%d%H%M%S)-$(openssl rand -hex 4)"
export DATA_BUCKET="cato-dashboard-data-$(date +%Y%m%d%H%M%S)-$(openssl rand -hex 4)"

# Create the buckets
aws s3 mb s3://$LAMBDA_BUCKET
aws s3 mb s3://$DATA_BUCKET
```

#### Step 3: Build and Upload Lambda Package

```bash
# Install dependencies and create zip package
cd src
python3 -m pip install -r requirements.txt -t .
zip -r security_hub_integration.zip lambda_function.py requests/ certifi/ charset_normalizer/ idna/ urllib3/
aws s3 cp security_hub_integration.zip s3://$LAMBDA_BUCKET/
cd ..
```

#### Step 4: Deploy with CloudFormation

```bash
aws cloudformation create-stack \
  --stack-name cato-dashboard \
  --template-body file://cloudformation/cato-dashboard-simplified.yaml \
  --parameters \
    ParameterKey=S3BucketName,ParameterValue=$DATA_BUCKET \
    ParameterKey=LambdaCodeBucket,ParameterValue=$LAMBDA_BUCKET \
    ParameterKey=LambdaCodeKey,ParameterValue=security_hub_integration.zip \
    ParameterKey=CreateS3Bucket,ParameterValue=false \
  --capabilities CAPABILITY_NAMED_IAM
```

#### Step 5: Monitor the Deployment

```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name cato-dashboard \
  --query 'Stacks[0].StackStatus'
```

The deployment typically takes 3-5 minutes. Once complete, Security Hub findings will be automatically collected and stored in the S3 bucket.

### Option 2: Full Deployment with QuickSight (Advanced)

For the full deployment including QuickSight dashboard setup, follow the instructions in the original Quick Start section below.

## How It Works

### Automated Data Flow

1. **Initial Data Collection:**
   - During CloudFormation deployment, the Lambda function is automatically invoked
   - It pulls all active NIST 800-53 findings from Security Hub
   - Processes the data into two CSV files:
     - `control_families.csv`: Summary statistics for each control family
     - `control_details.csv`: Detailed information for each control

2. **Real-time Updates:**
   - An EventBridge rule monitors for Security Hub finding changes
   - When findings are updated or imported, the Lambda is triggered
   - The Lambda regenerates the CSV files with fresh data
   - QuickSight automatically refreshes based on the schedule (default: 24 hours)

3. **Dashboard Visualization:**
   - The QuickSight dashboard displays key metrics:
     - Overall compliance rate
     - Compliance by control family
     - Control status distribution
     - Critical controls status
     - Risk distribution by severity

## Testing

To run the unit tests for the Lambda function:

```bash
# Install required packages
pip install pytest boto3 unittest-mock

# Run the tests
cd src
python -m pytest tests/test_lambda_function.py -v
python -m unittest test_custom_resource.py
```

Alternatively, you can use the provided test script:

```bash
./run_tests.sh
```

The tests verify the Lambda function's ability to:
- Process Security Hub findings correctly
- Extract control families from findings
- Calculate compliance percentages
- Handle edge cases and errors
- Properly respond to CloudFormation custom resource requests

## CI/CD Pipeline

This project includes a GitHub Actions workflow for continuous integration and deployment:

1. **Continuous Integration**:
   - Automatically runs tests on every push to the main branch and pull requests
   - Verifies that the Lambda function works correctly
   - Uploads test results as artifacts

2. **Continuous Deployment**:
   - Automatically deploys to the target GitHub repository when tests pass
   - Only runs on pushes to the main branch or manual workflow dispatch
   - Ensures that the target repository always has the latest working code

To deploy manually to the target repository:

```bash
./deploy.sh
```

This script will:
1. Run the tests to ensure everything works
2. Configure Git with the appropriate credentials
3. Push the code to the target repository

## Troubleshooting

### Common Issues and Solutions

1. **CloudFormation Stack Creation Stalling**
   - Check the Lambda function logs in CloudWatch
   - Verify that the Lambda has the correct permissions
   - Make sure Security Hub is enabled and accessible
   - If using the full template, consider the simplified version first

2. **Security Hub Findings Not Appearing**
   - Verify Security Hub is enabled with NIST 800-53 standard
   - Check the Lambda CloudWatch logs for errors
   - Manually invoke the Lambda function to refresh data:
     ```bash
     aws lambda invoke \
       --function-name cato-security-hub-integration \
       --payload '{}' \
       response.json
     ```

3. **Dashboard Creation Fails**
   - Increase the `WaitTimeForDashboardCreation` parameter
   - Check QuickSight permissions and access
   - Verify S3 bucket permissions

4. **QuickSight Data Refresh Issues**
   - Manually refresh the datasets in QuickSight
   - Check S3 access permissions for QuickSight
   - Verify CSV format in S3

## Security Considerations

- The CloudFormation template creates IAM roles with least-privilege permissions
- QuickSight access is restricted to authorized users only
- S3 bucket is configured with block public access enabled
- Security Hub integration uses encrypted connections
- Lambda function includes error handling and logging

## Maintenance

- QuickSight will automatically refresh the data based on the configured schedule
- Review and update user access permissions quarterly
- Monitor Lambda function performance through CloudWatch metrics
- Update the Lambda code if Security Hub API changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests before submitting a pull request
4. Submit a pull request with detailed description

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support:
1. Check the CloudWatch logs for the Lambda function
2. Review the documentation in `docs/`
3. Open an issue in the repository 