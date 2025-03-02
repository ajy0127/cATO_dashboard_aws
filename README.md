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
│   ├── deploy_dashboard.sh                # Script to automate dashboard deployment
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

- **Start with the Docs**: The `docs/deployment_guide.md` contains detailed instructions for deploying the solution
- **Testing**: Run `./scripts/run_tests.sh` to verify everything works before deploying
- **Core Logic**: The `src/lambda_function.py` file contains the main code that processes Security Hub findings
- **Sample Data**: The `samples/` directory contains example data to help you understand the format

## Overview

This solution automatically creates a comprehensive cATO dashboard by:

1. Deploying a Lambda function that pulls compliance data from AWS Security Hub
2. Transforming the data into a dashboard-friendly format and storing it in S3
3. Creating Athena databases and tables for efficient querying of security findings
4. Setting up automated updates via EventBridge when Security Hub findings change
5. Connecting Amazon Managed Grafana to Athena for visualization

## Deployment

For detailed deployment instructions, please refer to the [Deployment Guide](docs/deployment_guide.md).

The deployment process includes:
1. Setting up AWS resources using CloudFormation
2. Configuring Amazon Managed Grafana
3. Building compliance visualization dashboards

## Cost Considerations

Running the cATO Dashboard continuously involves costs for several AWS services. Here's an estimated monthly breakdown for a typical deployment:

### AWS Service Costs (Estimated Monthly)

| Service | Usage Pattern | Estimated Cost (USD) | Cost Factors |
|---------|---------------|----------------------|--------------|
| **AWS Lambda** | Daily invocations + Security Hub events | $5-15 | Function duration, memory allocation, number of findings |
| **Amazon S3** | Storage for findings data | $1-5 | Data volume, access frequency |
| **Amazon Athena** | Queries for dashboard visualization | $5-20 | Query frequency, data scanned per query |
| **Amazon Managed Grafana** | Dashboard hosting | $9-49 | Workspace tier, number of users |
| **AWS Security Hub** | Security findings source | $10-100+ | Number of accounts, resources monitored |
| **Amazon EventBridge** | Event routing | < $1 | Number of events processed |
| **CloudWatch Logs** | Lambda function logs | $1-5 | Log volume, retention period |
| **Total Estimated Monthly Cost** | | **$31-195+** | |

### Cost Optimization Tips

1. **Lambda Optimization**:
   - Adjust memory allocation based on actual usage patterns
   - Implement efficient code to reduce execution time

2. **Athena Query Optimization**:
   - Use partitioning for your security findings data
   - Write efficient queries with appropriate WHERE clauses
   - Consider using Athena workgroups with query result reuse

3. **S3 Storage Management**:
   - Implement lifecycle policies to archive older findings data
   - Consider compressing data for long-term storage

4. **Grafana Usage**:
   - Start with the Starter tier ($9/month) and upgrade only when needed
   - Limit the number of admin users

5. **Security Hub**:
   - Be selective about which security standards you enable
   - Consider aggregating findings from multiple accounts to a single monitoring account

### Cost Monitoring

Set up AWS Cost Explorer and create budget alerts to monitor your spending. You can also use the AWS Pricing Calculator to estimate costs based on your specific usage patterns: [AWS Pricing Calculator](https://calculator.aws/)

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

## Testing

To run the unit tests for the Lambda function:

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

## Troubleshooting

For troubleshooting guidance, please refer to the [Deployment Guide](docs/deployment_guide.md#troubleshooting).

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
