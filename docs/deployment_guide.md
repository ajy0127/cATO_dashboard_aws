# Deployment Guide for cATO Dashboard

This guide provides step-by-step instructions for deploying the cATO Dashboard with AWS Security Hub integration and Amazon Managed Grafana visualization.

## Prerequisites

Before you begin, make sure you have the following:

1. **AWS Account** with permissions to create IAM roles, Lambda functions, S3 buckets, Athena resources, and EventBridge rules
2. **AWS Security Hub** enabled with NIST 800-53 standard activated
3. **AWS CLI** installed and configured with appropriate access credentials
4. **Python 3.8+** installed (for local testing and development)

## Deployment Process

### Step 1: Clone the Repository

```bash
git clone https://github.com/ajy0127/cATO_dashboard_aws.git
cd cATO_dashboard_aws
```

### Step 2: Run the Deployment Script

The deployment script will guide you through setting up the entire cATO Dashboard solution:

```bash
chmod +x scripts/deploy_dashboard.sh
./scripts/deploy_dashboard.sh
```

The script will:
1. Create an S3 bucket for Lambda code
2. Create an S3 bucket for Security Hub findings data
3. Package and upload the Lambda function
4. Deploy the CloudFormation stack with Grafana integration
5. Set up initial data collection

### Step 3: Set up Amazon Managed Grafana

After the CloudFormation deployment completes:

1. Navigate to **Amazon Managed Grafana** in the AWS Console
2. Click **Create workspace**
3. Name it something meaningful like "Compliance-Dashboard"
4. For authentication, select **AWS IAM Identity Center**
5. Under service access, choose **Service managed** and select **Amazon Athena** and **CloudWatch**
6. Click **Create workspace** and wait for it to be created (5-10 minutes)

### Step 4: Configure Grafana Access

1. In your workspace details, go to the **Authentication** tab
2. Click **Assign new user or group**
3. Assign appropriate roles:
   - **Admin** - For GRC team leads and administrators
   - **Editor** - For team members who need to create/modify visualizations
   - **Viewer** - For executives, auditors, and stakeholders

### Step 5: Connect Grafana to Athena

1. Open your new Grafana workspace URL
2. After logging in, click the **Configuration** (gear) icon in the sidebar
3. Select **Data sources** and click **Add data source**
4. Find and select **Amazon Athena**
5. Configure it with:
   - **Name**: "cATO Compliance Findings"
   - **Authentication Provider**: AWS SDK Default
   - **Default Region**: Select your AWS region (MUST match your cATO deployment)
   - **Catalog**: AwsDataCatalog
   - **Database**: cato_security_findings_[timestamp] (check the actual name in Athena)
   - **Workgroup**: primary
   - **Output Location**: s3://cato-dashboard-data-[timestamp]-athena-results/
6. Click **Save & Test**

### Step 6: Create Your Dashboard

Follow the detailed instructions in the [Grafana Guide](grafana-guide.md) to:
1. Create dashboard variables for filtering
2. Build compliance visualization panels
3. Arrange your dashboard for maximum impact

> **Note:** The Grafana Guide focuses exclusively on building effective compliance dashboards and visualizations. It assumes you have already completed the setup steps in this deployment guide, including creating your Grafana workspace and connecting it to your Athena data source.

## Verifying Your Deployment

To verify that the deployment was successful:

1. Check that the Lambda function is running correctly:
```bash
aws lambda invoke --function-name cato-security-hub-integration-[timestamp] --payload '{}' response.json --profile your-profile
```

2. Check that data is being collected in the S3 bucket:
```bash
aws s3 ls s3://cato-dashboard-data-[timestamp]/ --recursive --profile your-profile
```

3. Verify that the Athena database and table were created:
```bash
aws athena list-databases --catalog-name AwsDataCatalog --profile your-profile
aws athena list-table-metadata --catalog-name AwsDataCatalog --database-name cato_security_findings_[timestamp] --profile your-profile
```

## Troubleshooting

### Common Issues

1. **CloudFormation Stack Creation Fails**
   - Check the CloudFormation Events tab in the AWS Console
   - Review error messages and make necessary adjustments

2. **No Data in Grafana**
   - Verify Security Hub is enabled with the NIST 800-53 standard
   - Check Lambda CloudWatch logs for errors
   - Verify Athena database and table were created correctly
   - Ensure Grafana has the correct permissions to access Athena

3. **Grafana Connection Issues**
   - Check IAM permissions for Grafana to access Athena
   - Verify region settings match between Grafana and your deployment
   - Double-check database and table names

### Viewing Lambda Logs

To view CloudWatch logs for troubleshooting Lambda issues:

```bash
aws logs get-log-events \
  --log-group-name /aws/lambda/cato-security-hub-integration-[timestamp] \
  --profile your-profile \
  --log-stream-name $(aws logs describe-log-streams \
    --log-group-name /aws/lambda/cato-security-hub-integration-[timestamp] \
    --profile your-profile \
    --order-by LastEventTime \
    --descending \
    --limit 1 \
    --query 'logStreams[0].logStreamName' \
    --output text)
```

### Cleaning Up Resources

If you need to delete the deployment:

```bash
# First empty the S3 buckets
aws s3 rm s3://cato-dashboard-data-[timestamp]/ --recursive --profile your-profile
aws s3 rm s3://cato-lambda-code-[timestamp]/ --recursive --profile your-profile

# Delete the CloudFormation stack
aws cloudformation delete-stack \
  --stack-name cato-dashboard \
  --profile your-profile
```

## Next Steps

After successful deployment:

1. Customize your Grafana dashboard for your organization's specific compliance needs
2. Set up regular reviews of your compliance data
3. Consider setting up alerts for critical compliance issues

For detailed instructions on building effective compliance visualizations, refer to the [Grafana Guide](grafana-guide.md). 