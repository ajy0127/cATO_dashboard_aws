# cATO Dashboard User Guide

This guide helps Information System Security Officers (ISSOs) and Authorizing Officials (AOs) utilize the cATO dashboard created via the CloudFormation template. The dashboard provides real-time visibility into your organization's NIST 800-53 compliance based on AWS Security Hub findings.

## Dashboard Overview

The cATO dashboard automatically displays compliance data from AWS Security Hub, with updates occurring in real-time as Security Hub findings change. The dashboard is organized into several key visualizations to help you quickly assess your compliance posture.

## Accessing the Dashboard

1. Log in to the AWS Management Console
2. Navigate to Amazon QuickSight
3. Find the "cATO Dashboard" under **Dashboards**
4. Click on the dashboard to open it

Alternatively, use the direct URL provided in the CloudFormation stack outputs:

```bash
aws cloudformation describe-stack-outputs \
  --stack-name cato-dashboard \
  --query 'Outputs[?OutputKey==`DashboardURL`].OutputValue' \
  --output text
```

## Understanding the Dashboard Visualizations

### 1. Overall Compliance Rate (KPI)

**Purpose**: Shows the percentage of controls that are compliant at a glance

- Green: >80% compliance (Good)
- Yellow: 50-80% compliance (Needs Attention)
- Red: <50% compliance (Critical)

This KPI represents the ratio of PASSED controls to total applicable controls across all control families.

### 2. Compliance by Control Family (Bar Chart)

**Purpose**: Highlights which control families need attention

Each bar represents a NIST 800-53 control family (e.g., AC for Access Control) with:
- Color-coded bars based on compliance percentage
- Length indicating compliance percentage
- Hover tooltips showing detailed metrics

Focus on red and yellow bars as they indicate areas requiring immediate attention.

### 3. Control Status Distribution (Donut Chart)

**Purpose**: Shows the breakdown of control statuses

The donut chart segments represent:
- PASSED (Green): Controls meeting requirements
- FAILED (Red): Non-compliant controls
- NOT_APPLICABLE (Gray): Controls not relevant to your environment
- UNKNOWN (Yellow): Controls with undetermined status

The center displays the total number of controls evaluated.

### 4. Critical Controls Table

**Purpose**: Highlights high-priority controls requiring attention

This table is filtered to show only CRITICAL severity controls with:
- Control ID (e.g., AC-2)
- Control Family
- Current Status
- Severity
- Description

Sort by Status to quickly identify failed critical controls.

### 5. Risk Distribution (Heat Map)

**Purpose**: Visualizes risk concentration across families and severity levels

The heat map shows:
- Rows: Control families
- Columns: Severity levels (CRITICAL, HIGH, MEDIUM, LOW)
- Color intensity: Number of controls in each category

Dark red cells indicate areas with the highest concentration of risks.

## Using the Dashboard Effectively

### Interactive Filtering

Use the filters at the top of the dashboard to:
1. **Filter by Control Family**: Focus on specific control families
2. **Filter by Status**: View only failed or passed controls
3. **Filter by Severity**: Focus on critical and high severity controls

Filters apply across all visualizations for consistent analysis.

### Data Exploration

1. **Cross-filtering**: Click on elements in one visual to filter other visuals
   - Example: Click on a family in the bar chart to see only that family's controls in other visuals

2. **Drill-downs**: Click on specific elements to view more detailed information
   - Example: Click on a FAILED segment in the donut chart to see all failed controls in the table

3. **Exporting**: Export visualizations or data:
   - Click the menu icon (...) on any visual
   - Select "Export to CSV" or "Export as image"

### Regular Monitoring Activities

For ISSOs and AOs:

1. **Daily Checks**:
   - Review the Overall Compliance KPI for changes
   - Check Critical Controls Table for any new failed controls
   - Monitor the Control Family chart for declining trends

2. **Weekly Analysis**:
   - Review Control Status Distribution for shifts in compliance
   - Analyze Risk Distribution heat map for emerging risk areas
   - Export reports for team reviews

3. **Monthly Review**:
   - Document compliance trends over time
   - Identify persistent problem areas
   - Develop remediation plans for consistently failing controls

## Understanding Data Updates

The dashboard is automatically updated as new findings appear in Security Hub:

1. **Real-time Triggers**: New Security Hub findings trigger Lambda updates
2. **Scheduled Refreshes**: QuickSight datasets refresh every 24 hours (configurable)
3. **Manual Refresh**: Force a refresh by:
   - Going to the QuickSight Datasets page
   - Finding the cATO datasets
   - Clicking "Refresh Now"

## Troubleshooting Dashboard Issues

### Common Visualization Issues

1. **No Data Appears**:
   - Verify Security Hub has active findings
   - Check Lambda execution logs for errors
   - Confirm QuickSight permissions are correct

2. **Stale Data**:
   - Check when data was last refreshed (timestamp on dashboard)
   - Manually refresh datasets if needed
   - Verify EventBridge rule is active

3. **Visual Formatting Issues**:
   - Try refreshing your browser
   - Clear browser cache
   - Access from another browser if problems persist

## Advanced Usage

### Creating Custom Visuals

To create additional visualizations:
1. Click "Edit" on the dashboard
2. Click "Add" > "Add visual"
3. Select the appropriate visual type
4. Configure using the fields from the datasets
5. Format to match existing visual styles
6. Save the dashboard

### Sharing and Reporting

1. **Share the Dashboard**:
   - Click "Share" in the top right
   - Add users or groups
   - Set appropriate permissions

2. **Schedule Email Reports**:
   - Click "Reports" in QuickSight
   - Create a new report based on the dashboard
   - Set schedule (e.g., weekly summary)
   - Add recipients

3. **Embed in Internal Portals**:
   - Use QuickSight embedding capabilities
   - Get embed code: Dashboard menu > "Share" > "Embed dashboard"
   - Follow instructions to embed in your internal portal

## Support and Resources

- For dashboard functionality issues: Contact your AWS QuickSight administrator
- For compliance questions: Consult your organization's security team
- For technical support: Check CloudWatch logs for the Lambda function

## Additional Resources

- [AWS Security Hub Documentation](https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html)
- [NIST 800-53 Controls Reference](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [QuickSight User Guide](https://docs.aws.amazon.com/quicksight/latest/user/welcome.html) 