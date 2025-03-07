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
4. For authentication, select **AWS IAM Identity Center** (recommended) or a SAML 2.0 compatible identity provider
5. Under service access, choose **Service managed** and select **Amazon Athena** and **CloudWatch**
6. Ensure you're creating the workspace in a supported region (US East, US West, Asia Pacific, or Europe regions)
7. Click **Create workspace** and wait for it to be created (5-10 minutes)

> **Note:** Amazon Managed Grafana is available in specific AWS regions including US East (Ohio), US East (N. Virginia), US West (Oregon), Asia Pacific (Seoul, Singapore, Sydney, Tokyo), and Europe (Frankfurt, Ireland, London). Ensure you deploy in a supported region.

### Step 4: Configure Grafana Access

1. In your workspace details, go to the **Authentication** tab
2. Click **Assign new user or group**
3. Assign appropriate roles:
   - **Admin** - For GRC team leads and administrators who need to manage the workspace
   - **Editor** - For team members who need to create/modify visualizations
   - **Viewer** - For executives, auditors, and stakeholders who only need to view dashboards

> **Note:** If using IAM Identity Center, ensure it's properly configured in your AWS account. If using SAML, you'll need to configure your identity provider with the appropriate metadata and attribute mappings. Refer to the [Amazon Managed Grafana Authentication documentation](https://docs.aws.amazon.com/grafana/latest/userguide/authentication-in-AMG.html) for detailed instructions.

### Step 5: Connect Grafana to Athena

1. Open your new Grafana workspace URL
2. After logging in, navigate to the left sidebar and click on **Apps**
3. Scroll down to find **Athena** in the list of available apps
4. Click the **Install now** button next to Athena
5. Once installed, click on **Connections** in the left sidebar
6. Click **Add new connection** and select **Data sources**
7. Find and select **Amazon Athena**
8. Configure it with:
   - **Name**: "cATO Compliance Findings"
   - **Authentication Provider**: AWS SDK Default
   - **Default Region**: Select your AWS region (MUST match your cATO deployment)
   - **Catalog**: AwsDataCatalog
   - **Database**: cato_security_findings_[timestamp] (check the actual name in Athena)
   - **Workgroup**: primary
   - **Output Location**: s3://cato-dashboard-data-[timestamp]-athena-results/
9. Click **Save & Test**

> **Note:** Amazon Managed Grafana uses AWS service roles to access AWS services. Ensure your Grafana workspace has the necessary permissions to access Athena and S3. You can modify the service role permissions in the IAM console if needed. For more details, refer to the [Amazon Managed Grafana Data Source Management documentation](https://docs.aws.amazon.com/grafana/latest/userguide/AMG-manage-data-source.html).

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

## CloudFormation Template for Grafana with Basic Authentication

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'cATO Dashboard with Self-Hosted Grafana'

Parameters:
  AdminUsername:
    Type: String
    Default: 'admin'
    Description: Username for Grafana admin user
  
  AdminPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    Description: Password for Grafana admin user
    ConstraintDescription: Must be at least 8 characters
  
  ViewerUsername:
    Type: String
    Default: 'viewer'
    Description: Username for Grafana viewer user
  
  ViewerPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    Description: Password for Grafana viewer user
    ConstraintDescription: Must be at least 8 characters
  
  InstanceType:
    Type: String
    Default: 't3.small'
    AllowedValues: ['t3.micro', 't3.small', 't3.medium']
    Description: EC2 Instance type for Grafana server

Resources:
  # Security Group for Grafana instance
  GrafanaSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for Grafana server
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 3000
          ToPort: 3000
          CidrIp: 0.0.0.0/0
  
  # IAM Role for Grafana to access AWS resources
  GrafanaRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonAthenaFullAccess
        - arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
  
  # Instance Profile
  GrafanaInstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref GrafanaRole
  
  # EC2 Instance for Grafana
  GrafanaInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: ami-0261755bbcb8c4a84  # Amazon Linux 2023 (us-east-1)
      SecurityGroupIds:
        - !GetAtt GrafanaSecurityGroup.GroupId
      IamInstanceProfile: !Ref GrafanaInstanceProfile
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash -xe
          
          # Update system packages
          dnf update -y
          
          # Install Docker
          dnf install -y docker
          systemctl enable docker.service
          systemctl start docker.service
          
          # Create directories for Grafana persistence
          mkdir -p /grafana/data /grafana/dashboards /grafana/provisioning
          
          # Create provisioning directories
          mkdir -p /grafana/provisioning/datasources
          mkdir -p /grafana/provisioning/dashboards
          
          # Create data source configuration for Athena
          cat > /grafana/provisioning/datasources/athena.yaml << 'EOL'
          apiVersion: 1
          datasources:
            - name: AWS Athena
              type: grafana-athena-datasource
              access: proxy
              isDefault: true
              jsonData:
                authType: default
                defaultRegion: ${AWS::Region}
                catalog: AwsDataCatalog
                database: security_findings_db
                workgroup: primary
          EOL
          
          # Create dashboard provisioning configuration
          cat > /grafana/provisioning/dashboards/default.yaml << 'EOL'
          apiVersion: 1
          providers:
            - name: 'default'
              orgId: 1
              folder: 'cATO Dashboards'
              type: file
              disableDeletion: false
              editable: true
              updateIntervalSeconds: 30
              allowUiUpdates: true
              options:
                path: /var/lib/grafana/dashboards
          EOL
          
          # Create Executive Summary Dashboard
          cat > /grafana/dashboards/executive-summary.json << 'EOL'
          {
            "annotations": {
              "list": [ ]
            },
            "editable": true,
            "fiscalYearStartMonth": 0,
            "graphTooltip": 0,
            "id": 1,
            "links": [],
            "liveNow": false,
            "panels": [
              {
                "datasource": {
                  "type": "grafana-athena-datasource",
                  "uid": "P8E80F9AEF21F6940"
                },
                "description": "Overall compliance percentage across all controls",
                "fieldConfig": {
                  "defaults": {
                    "color": {
                      "mode": "thresholds"
                    },
                    "mappings": [],
                    "max": 100,
                    "min": 0,
                    "thresholds": {
                      "mode": "absolute",
                      "steps": [
                        {
                          "color": "red",
                          "value": null
                        },
                        {
                          "color": "yellow",
                          "value": 50
                        },
                        {
                          "color": "green",
                          "value": 80
                        }
                      ]
                    },
                    "unit": "percent"
                  },
                  "overrides": []
                },
                "gridPos": {
                  "h": 8,
                  "w": 12,
                  "x": 0,
                  "y": 0
                },
                "id": 1,
                "options": {
                  "orientation": "auto",
                  "reduceOptions": {
                    "calcs": [
                      "lastNotNull"
                    ],
                    "fields": "",
                    "values": false
                  },
                  "showThresholdLabels": false,
                  "showThresholdMarkers": true
                },
                "pluginVersion": "9.3.6",
                "targets": [
                  {
                    "connectionArgs": {
                      "catalog": "AwsDataCatalog",
                      "database": "security_findings_db",
                      "region": "${AWS::Region}",
                      "resultReuseEnabled": true,
                      "workgroup": "primary"
                    },
                    "format": 1,
                    "rawSQL": "SELECT COUNT(CASE WHEN status = 'PASSED' THEN 1 END) * 100.0 / COUNT(*) as compliance_rate FROM security_findings",
                    "refId": "A"
                  }
                ],
                "title": "Overall Compliance Rate",
                "type": "gauge"
              }
            ],
            "refresh": "1h",
            "schemaVersion": 38,
            "style": "dark",
            "tags": ["security", "compliance"],
            "templating": {
              "list": []
            },
            "time": {
              "from": "now-30d",
              "to": "now"
            },
            "timepicker": {},
            "timezone": "",
            "title": "cATO Executive Summary",
            "uid": "cato-exec-summary",
            "version": 1
          }
          EOL
          
          # Run Grafana with our configuration
          docker run -d \
            --name=grafana \
            -p 3000:3000 \
            -v /grafana/data:/var/lib/grafana \
            -v /grafana/provisioning:/etc/grafana/provisioning \
            -v /grafana/dashboards:/var/lib/grafana/dashboards \
            -e "GF_SECURITY_ADMIN_USER=${AdminUsername}" \
            -e "GF_SECURITY_ADMIN_PASSWORD=${AdminPassword}" \
            -e "GF_AUTH_BASIC_ENABLED=true" \
            -e "GF_AUTH_ANONYMOUS_ENABLED=false" \
            -e "GF_INSTALL_PLUGINS=grafana-athena-datasource" \
            grafana/grafana-oss:latest
          
          # Wait for Grafana to start
          sleep 30
          
          # Create viewer user via API
          curl -X POST -H "Content-Type: application/json" \
            -d "{\"name\":\"Viewer User\",\"email\":\"viewer@example.com\",\"login\":\"${ViewerUsername}\",\"password\":\"${ViewerPassword}\",\"OrgId\":1,\"role\":\"Viewer\"}" \
            http://${AdminUsername}:${AdminPassword}@localhost:3000/api/admin/users
          
          # Install cfn-signal
          dnf install -y aws-cfn-bootstrap
          
          # Signal CloudFormation that setup is complete
          /opt/aws/bin/cfn-signal -e $? --stack ${AWS::StackName} --resource GrafanaInstance --region ${AWS::Region}
      
      Tags:
        - Key: Name
          Value: Grafana-cATO-Dashboard
      
      CreationPolicy:
        ResourceSignal:
          Timeout: PT15M

Outputs:
  GrafanaURL:
    Description: URL to access Grafana
    Value: !Sub http://${GrafanaInstance.PublicDnsName}:3000
    
  GrafanaAdminUser:
    Description: Grafana admin username
    Value: !Ref AdminUsername
    
  GrafanaViewerUser:
    Description: Grafana viewer username
    Value: !Ref ViewerUsername 