[![CI/CD Pipeline for cATO Dashboard](https://github.com/ajy0127/cATO_dashboard_aws/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/ajy0127/cATO_dashboard_aws/actions/workflows/ci-cd.yml)

# cATO Dashboard Project

This project provides infrastructure-as-code and documentation for setting up a continuous Authority to Operate (cATO) dashboard using Amazon Managed Grafana with automated data integration from AWS Security Hub via Amazon Athena. The dashboard helps Information System Security Officers (ISSOs) and Authorizing Officials (AOs) monitor NIST 800-53 compliance in real-time.

## Project Structure

```
.
├── README.md                              # This file - Start here!
├── cloudformation/                        # AWS Infrastructure as Code
│   └── cato-dashboard.yaml                # CloudFormation template with Grafana integration
├── docs/                                  # Documentation
│   ├── deployment_guide.md                # Step-by-step deployment instructions
│   └── grafana-guide.md                   # Guide for building visualizations in Grafana
├── samples/                               # Sample data and configuration files
│   ├── findings.json                      # Example Security Hub findings
│   ├── cato-manifest.json                 # Manifest file for data organization
│   └── security_hub_integration.zip       # Sample Lambda deployment package
├── scripts/                               # Helper scripts
│   ├── deploy.sh                          # Deployment script
│   ├── deploy_dashboard.sh                # Script to automate Grafana dashboard setup
│   ├── run_tests.sh                       # Script to run automated tests locally
│   └── run_cfn_lint.sh                    # Script to validate CloudFormation templates
├── src/                                   # Source code
│   ├── lambda_function.py                 # Main Lambda code that processes Security Hub findings
│   └── requirements.txt                   # Python dependencies
├── tests/                                 # Automated tests
│   ├── test_lambda_function.py            # Unit tests for the Lambda function
│   └── test_custom_resource.py            # Tests for CloudFormation custom resources
└── .github/                               # CI/CD configuration
    └── workflows/                         # GitHub Actions workflows
        └── ci-cd.yml                      # Continuous integration and deployment
```

### Key Components for Beginners

- **Start with the Docs**: The `docs/` directory contains detailed guides for deployment and dashboard setup
- **Testing**: Run `./scripts/run_tests.sh` to verify everything works before deploying
- **Core Logic**: The `src/lambda_function.py` file contains the main code that processes Security Hub findings
- **Sample Data**: The `samples/` directory contains example data to help you understand the format

### Folder Explanation

1. **CloudFormation Template**
   - This template defines your AWS infrastructure (S3 buckets, Lambda functions, IAM roles, etc.)
   - Includes Grafana integration for visualization

2. **Documentation**
   - Comprehensive guides for deployment and visualization
   - Step-by-step instructions with screenshots

3. **Source Code**
   - Lambda function that integrates with Security Hub
   - Python dependencies listed in requirements.txt

4. **Tests**
   - Automated tests to verify functionality
   - Run with the provided script in the scripts directory

5. **Scripts**
   - Helper scripts to simplify deployment, testing, and validation
   - Run from the root directory (e.g., `./scripts/run_tests.sh`)

6. **Samples**
   - Example data and configuration files
   - Useful for understanding the expected format and structure

## Overview

This solution automatically creates a comprehensive cATO dashboard by:

1. Deploying a Lambda function that pulls compliance data from AWS Security Hub
2. Transforming the data into a dashboard-friendly format and storing it in S3
3. Creating Athena databases and tables for efficient querying of security findings
4. Setting up automated updates via EventBridge when Security Hub findings change
5. Providing instructions for connecting Amazon Managed Grafana to Athena for visualization

## Recent Updates

The codebase has been improved with the following changes:

1. **Amazon Managed Grafana Integration**: Using Amazon Managed Grafana for visualization capabilities, customization options, and enhanced interactivity.

2. **Grafana Annotations**: Added the ability for the Lambda function to create Grafana annotations when new findings are processed, making it easier to track when data was updated.

3. **Amazon Athena Integration**: Added integration with Amazon Athena to provide SQL query capabilities over security findings data, enabling more powerful analysis and visualization.

4. **JSONL Format for Findings**: The Lambda function now stores findings in JSONL format (one JSON object per line) to improve compatibility with Athena.

5. **Automated Athena Setup**: CloudFormation template now includes resources to automatically create Athena databases and tables.

6. **Daily Scheduled Updates**: Added a scheduled EventBridge rule to collect findings daily, ensuring the dashboard data stays current.

7. **Enhanced CloudFormation Support**: The Lambda function now properly handles CloudFormation custom resource requests, ensuring smoother and more reliable deployments.

8. **Conditional S3 Bucket Creation**: The CloudFormation template now includes a parameter to decide whether to create a new S3 bucket or use an existing one.

9. **Improved Error Handling**: The Lambda function has better error handling and logging to help troubleshoot issues.

## Why Grafana?

Amazon Managed Grafana provides several advantages for security compliance visualization:

1. **Rich Visualization Options**: More chart types and visualization options, including heatmaps, gauges, and more.

2. **Open-Source Compatibility**: Use existing Grafana dashboards and plugins from the community.

3. **Multi-Data Source Support**: Connect to Athena, CloudWatch, and many other data sources simultaneously in the same dashboard.

4. **Alerting Capabilities**: Create and manage alerts directly from your dashboards with built-in alerting system.

5. **Annotation Support**: Mark important events on your time-series visualizations.

6. **Interactive Dashboards**: More interactive elements and dynamic variables for filtering and exploring data.

## Why Athena?

Amazon Athena provides several advantages for analyzing security findings:

1. **SQL Query Capability**: Query your security findings using standard SQL without setting up or maintaining databases.

2. **Cost-Effective**: Pay only for the queries you run, with no upfront costs or ongoing infrastructure to maintain.

3. **Serverless**: No servers to provision or manage; just point Athena at your S3 buckets and start querying.

4. **Performance**: Athena's distributed query engine provides fast results even on large datasets.

5. **Grafana Integration**: Seamless integration with Amazon Managed Grafana for visualization and dashboarding.

6. **Schema Evolution**: As your data changes, Athena can adapt without breaking existing dashboards.

## Your First Adventure

Want to jump right in? Here's your GRC-to-cloud engineering adventure path:

1. **Setup AWS Environment**: Make sure you have AWS CLI configured and access to create resources (15 mins).
2. **Enable Security Hub**: Make sure Security Hub is enabled in your AWS account—this is where all your compliance findings will come from!
3. **Launch the Stack**: Fire off the CloudFormation template—boom, your security data pipeline is live!
4. **Craft Your Dashboard**: Follow the guide to build your first visualization and grab some screenshots for your portfolio.

Detailed steps are provided in the Quick Start section below, but this is your big-picture journey!

## Prerequisites

- AWS Account with the following services enabled:
  - AWS Security Hub with NIST 800-53 standard enabled
  - AWS Lambda, CloudFormation, and Athena
  - Amazon Managed Grafana workspace (for dashboard visualization)
- IAM permissions to create roles, Lambda functions, and S3 buckets
- AWS CLI configured with appropriate credentials

## Quick Start

### Option 1: Simplified Deployment (Security Hub Integration Only)

This option sets up the automated data collection from Security Hub without Grafana integration.

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
pip install grafana-client -t .
zip -r security_hub_integration.zip lambda_function.py requests/ certifi/ charset_normalizer/ idna/ urllib3/ grafana_client/
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
    ParameterKey=GrafanaIntegration,ParameterValue=false \
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

### Option 2: Full Deployment with Grafana Integration

To deploy with Grafana integration:

1. First, set up an Amazon Managed Grafana workspace following the instructions in `docs/grafana-guide.md`.

2. Create an API key in your Grafana workspace:
   - Navigate to your Grafana workspace
   - Go to Configuration > API Keys
   - Create a new API key with Admin permissions
   - Copy the API key (you won't be able to see it again)

3. Deploy the CloudFormation stack with Grafana parameters:

```bash
aws cloudformation create-stack \
  --stack-name cato-dashboard \
  --template-body file://cloudformation/cato-dashboard-simplified.yaml \
  --parameters \
    ParameterKey=S3BucketName,ParameterValue=$DATA_BUCKET \
    ParameterKey=LambdaCodeBucket,ParameterValue=$LAMBDA_BUCKET \
    ParameterKey=LambdaCodeKey,ParameterValue=security_hub_integration.zip \
    ParameterKey=CreateS3Bucket,ParameterValue=false \
    ParameterKey=GrafanaIntegration,ParameterValue=true \
    ParameterKey=GrafanaURL,ParameterValue=https://your-grafana-workspace-url \
    ParameterKey=GrafanaAPIKey,ParameterValue=your-api-key \
    ParameterKey=GrafanaDashboardID,ParameterValue=your-dashboard-id \
  --capabilities CAPABILITY_NAMED_IAM
```

4. Follow the instructions in `docs/grafana-guide.md` to set up your dashboard.

## How It Works

### Automated Data Flow

1. **Initial Data Collection:**
   - During CloudFormation deployment, the Lambda function is automatically invoked
   - It pulls all active NIST 800-53 findings from Security Hub
   - Processes the data into JSONL format and stores it in S3
   - Sets up Athena database and table for querying the findings

2. **Real-time Updates:**
   - An EventBridge rule monitors for Security Hub finding changes
   - When findings are updated or imported, the Lambda is triggered
   - The Lambda regenerates the JSONL files with fresh data
   - If Grafana integration is enabled, the Lambda also creates annotations
   - Grafana dashboards can be set to auto-refresh at desired intervals

3. **Dashboard Visualization:**
   - The Grafana dashboard displays key metrics:
     - Overall compliance rate
     - Compliance by product/service
     - Control status distribution
     - Critical controls status
     - Risk distribution by severity

## Testing

To run the unit tests for the Lambda function:

```bash
# Install required packages
pip install pytest boto3 mock

# Run the tests
cd src
python -m pytest tests/test_lambda_function.py -v
python -m unittest test_custom_resource.py
```

To run CloudFormation template linting:

```bash
# Install cfn-lint
pip install cfn-lint

# Run linting on all CloudFormation templates
cfn-lint cloudformation/*.yaml
```

Alternatively, you can use the provided test scripts:

```bash
# Run all tests including Lambda tests and CloudFormation linting
./scripts/run_tests.sh

# Run only CloudFormation linting
./scripts/run_cfn_lint.sh
```

The tests verify the Lambda function's ability to:
- Process Security Hub findings correctly
- Extract control families from findings
- Calculate compliance percentages
- Handle edge cases and errors
- Properly respond to CloudFormation custom resource requests

The CloudFormation linting checks:
- Syntax errors in templates
- Best practices for AWS resources
- Resource property validation
- IAM policy validation
- Security best practices

## Running Tests for Beginners

Not familiar with automated testing? No problem! Testing is a great way to make sure everything works before you deploy your dashboard. Think of tests as automatic checks that verify your code works correctly.

### Why Run Tests?

- **Catch Problems Early**: Find issues before deploying to AWS
- **Save Time and Money**: Avoid troubleshooting in the AWS console
- **Build Confidence**: Know your changes work before deploying

### How to Run Tests (Easy Mode)

1. Make sure you have Python installed on your computer
2. Open a terminal and navigate to the project directory
3. Run this command:

```bash
./scripts/run_tests.sh
```

This script will:
- Create a virtual environment (a clean Python setup)
- Install all needed packages
- Set up test data
- Run all tests
- Show you if anything failed

### Understanding Test Results

- **Green "PASSED"**: The feature works as expected! 
- **Red "FAILED"**: Something needs fixing before deploying

### What to Do If Tests Fail

1. Read the error message - it usually points to what's wrong
2. Check if you've modified any files in the `src/` directory
3. Ask for help in the GitHub issues section

Running tests is a professional practice used by GRC engineers and shows you're taking a systematic approach to security - a great talking point for interviews!

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
./scripts/deploy.sh
```

This script will:
1. Run the tests to ensure everything works
2. Configure Git with the appropriate credentials
3. Push the code to the target repository

## Troubleshooting

### Common Issues and Solutions

1. **CloudFormation Stack Creation Stalling or Failing**
   - Check the Lambda function logs in CloudWatch
   - Verify that the Lambda has the correct permissions
   - Make sure Security Hub is enabled and accessible
   - If using the full template, consider the simplified version first
   - **EventBridge Rule Name Length**: AWS EventBridge rule names have a 64-character limit. If your deployment generates long names (especially with timestamps and random suffixes), the deployment may fail. The template has been updated to use shorter names, but if you're using a custom version, ensure rule names are within limits.

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

3. **Grafana Dashboard Issues**
   - Verify data source connection to Athena
   - Check IAM permissions for Grafana to access Athena
   - Ensure the SQL queries are formatted correctly
   - Verify the database and table names match what is in Athena

4. **Grafana Annotations Not Appearing**
   - Check that the Grafana API key has sufficient permissions
   - Verify the Grafana URL is correct and accessible from the Lambda
   - Check the Lambda function logs for any errors related to the Grafana API

5. **Athena Query Failures**
   - Ensure the JSONL format in S3 is correct (one JSON object per line)
   - Check that the Athena database and table were created successfully
   - Verify S3 permissions for Athena
