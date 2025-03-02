# GRC Professional's Guide to Amazon Managed Grafana for cATO Dashboard

Welcome, GRC professional! This guide will help you create compelling visualizations of your Security Hub findings that will help you demonstrate compliance, track remediation efforts, and communicate risk effectively to stakeholders.

> **Note:** This guide assumes you have already completed the setup steps in the [Deployment Guide](deployment_guide.md), including creating your Grafana workspace and connecting it to your Athena data source.

## Why Grafana Will Transform Your GRC Program

1. **Compliance Visualization at Scale** - Amazon Managed Grafana provides access to over 100 data source plugins, allowing you to create visualization types that make complex compliance data immediately understandable. Heat maps, gauges, and geo maps will help executives quickly grasp your compliance posture.
  
2. **Holistic Risk View** - Amazon Managed Grafana supports multiple AWS services as data sources, including Amazon Athena, AWS CloudWatch, Amazon OpenSearch Service, AWS IoT SiteWise, and Amazon Timestream. This allows you to combine compliance status, security events, and business risk in a single dashboard.

3. **Real-time Compliance Monitoring** - With Amazon Managed Grafana's support for automatic data refresh and alerting, your compliance dashboards stay current. No more "this assessment is from last quarter" conversations with auditors.

4. **Automated Risk Alerting** - Amazon Managed Grafana includes built-in alerting capabilities that allow you to set thresholds for compliance metrics and get notified when they breach acceptable levels.

5. **Document Control Activities with Annotations** - Mark key compliance events directly on time-series data using Grafana's annotation feature. This is invaluable for demonstrating control effectiveness to auditors and leadership.

6. **Enterprise-Grade Security** - Amazon Managed Grafana integrates with AWS IAM Identity Center and supports SAML 2.0 for authentication, ensuring secure access to your compliance dashboards.

## Building Effective Compliance Dashboards

Now that your Grafana workspace is set up and connected to your compliance data (as outlined in the Deployment Guide), let's focus on creating dashboards that drive compliance decisions.

> **Important:** The Grafana interface may have changed since this guide was written. You'll need to first install the Athena plugin from the Apps section before you can connect to your compliance data. Follow the steps in the Deployment Guide for the most up-to-date instructions.

### Step 1: Create Dashboard Variables - Where GRC Professionals Excel

Variables make your dashboard interactive and powerful for risk-based decision making. Amazon Managed Grafana supports various types of variables including query variables, custom variables, and text box variables.

1. Create a new dashboard by clicking on **Dashboards** in the left sidebar and then **+ New Dashboard**
2. Click the gear icon in the top right for dashboard settings
3. Go to the **Variables** tab and click **Add variable**
4. For each variable, select the type **Query** and configure:
   - **Name**: The variable name (e.g., "severity")
   - **Label**: The display name (e.g., "Severity")
   - **Data source**: Your Athena data source
   - **Query**: The SQL query (examples below)
   - **Selection options**: Enable "Include All option" and "Multi-value" for flexibility

**Severity Variable**:
```sql
SELECT DISTINCT severity FROM security_findings 
ORDER BY CASE 
  WHEN severity = 'CRITICAL' THEN 1 
  WHEN severity = 'HIGH' THEN 2 
  WHEN severity = 'MEDIUM' THEN 3 
  WHEN severity = 'LOW' THEN 4 
  ELSE 5 
END
```

**Status Variable**:
```sql
SELECT DISTINCT status FROM security_findings ORDER BY status
```

**Product Variable**:
```sql
SELECT DISTINCT product_name FROM security_findings ORDER BY product_name
```

Pro tip: Always enable multi-select and "All" options for your variables. This gives your stakeholders the flexibility to drill down into specific risk areas or see the big picture without needing separate dashboards.

### Step 2: Build Insightful Compliance Panels - The Risk Communication Part

Amazon Managed Grafana supports a wide range of visualization types. Here's how to create panels that drive compliance decisions:

1. Click **Add panel** in your dashboard
2. Select the visualization type appropriate for your data (e.g., Stat, Bar chart, Pie chart)
3. Configure the data source as your Athena connection
4. Enter the SQL query (examples below)
5. Use the panel options to customize appearance, thresholds, and other settings

#### The Executive Summary KPI

Every executive and auditor wants this number first - overall compliance percentage:

```sql
SELECT COUNT(CASE WHEN status = 'PASSED' THEN 1 END) * 100.0 / COUNT(*) as compliance_rate
FROM security_findings
WHERE severity IN (${severity:sqlstring}) AND status IN (${status:sqlstring}) AND product_name IN (${product:sqlstring})
```

Style it with intuitive thresholds: 0-50% red, 50-80% yellow, 80-100% green. This creates immediate visual understanding of compliance status.

#### The Service Owner's Accountability Chart

This horizontal bar chart shows compliance by product, making it clear which teams need remediation focus:

```sql
SELECT 
  product_name, 
  COUNT(CASE WHEN status = 'PASSED' THEN 1 END) * 100.0 / COUNT(*) as compliance_rate
FROM security_findings
WHERE severity IN (${severity:sqlstring}) AND status IN (${status:sqlstring}) AND product_name IN (${product:sqlstring})
GROUP BY product_name
ORDER BY compliance_rate ASC
```

GRC trick: Ordering by compliance_rate ASC puts the worst performers at the top - this focuses remediation attention exactly where it's needed.

#### Control Status Distribution - The Auditor's Favorite

This donut chart gives auditors a quick view of control status distribution:

```sql
SELECT 
  status, 
  COUNT(*) as count
FROM security_findings
WHERE severity IN (${severity:sqlstring}) AND status IN (${status:sqlstring}) AND product_name IN (${product:sqlstring})
GROUP BY status
```

A lesson from experience: Use consistent colors across your dashboard for status values. If "PASSED" is green in one chart, make sure it's green everywhere. Consistency is key for effective compliance communication.

#### The Risk-Focused Controls Table

This table highlights your critical controls - the ones that keep CISOs and compliance officers up at night:

```sql
SELECT 
  id,
  product_name,
  title,
  status,
  severity,
  description
FROM security_findings
WHERE severity = 'CRITICAL' AND severity IN (${severity:sqlstring}) AND status IN (${status:sqlstring}) AND product_name IN (${product:sqlstring})
ORDER BY status DESC
```

GRC insight: In my early days, I'd try to show ALL the controls. Focus on what matters - critical severity items get immediate attention and action. This risk-based approach is what modern compliance programs are built on.

#### The Risk Heat Map - Your Compliance Secret Weapon

This visualization changed my GRC career - it shows exactly where risk concentrates across your environment:

```sql
SELECT 
  product_name,
  severity,
  COUNT(*) as count
FROM security_findings
WHERE severity IN (${severity:sqlstring}) AND status IN (${status:sqlstring}) AND product_name IN (${product:sqlstring})
GROUP BY product_name, severity
ORDER BY 
  CASE 
    WHEN severity = 'CRITICAL' THEN 1 
    WHEN severity = 'HIGH' THEN 2 
    WHEN severity = 'MEDIUM' THEN 3 
    WHEN severity = 'LOW' THEN 4 
    ELSE 5 
  END,
  product_name
```

A color scheme from red (high) to green (low) intuitively shows risk concentration. This visualization has helped me identify systemic compliance issues that would have been invisible in tables or charts.

### Step 3: Arranging Your Dashboard for Maximum Compliance Impact

Dashboard layout is risk storytelling. Here's the narrative flow I've found most effective over years of presenting to executives and auditors:

1. Place your Overall Compliance KPI at the top - this answers the first question everyone asks
2. Position the Compliance by Product and Status Distribution side by side - they complement each other
3. Place the Risk Heat Map prominently - it's visually engaging and information-dense
4. Put the Critical Controls table at the bottom - it's detailed information for those who want to dig deeper into specific control failures

Remember to save your dashboard frequently! Nothing is worse than losing an hour of work because you forgot to save.

### Step 4: Set Up Auto-Refresh (But Be Smart About It)

After years of manually refreshing compliance dashboards before audit meetings, auto-refresh feels like magic:

1. Click the time range selector in the dashboard navigation
2. Set an appropriate refresh interval based on your data update frequency

GRC wisdom: Don't set refresh too frequently! If your compliance data updates daily, a 1-hour refresh is plenty. Excessive refreshing creates unnecessary load and can even incur higher costs.

### Step 5: Sharing Your Dashboard - Making Your Compliance Work Count

The most beautiful compliance dashboard provides zero value if the right stakeholders can't see it:

1. Click the share icon in the top navigation
2. For regular stakeholders, make sure they have Viewer access to the workspace
3. For occasional sharing, consider:
   - Creating a snapshot (great for distributing a point-in-time compliance view)
   - Exporting to PDF for inclusion in audit reports
   - Setting up email reports for executives and auditors

Pro tip: Before important audit meetings, always check your dashboard access by opening an incognito browser window and logging in as a viewer. I've had too many "let me just share my screen instead" moments in my compliance career!

## Taking It Further: Automating with Python

Want to really impress your audit team? Here's how to update your Lambda function to automatically add annotations to your dashboard when new findings are processed:

```python
def update_grafana_dashboard(findings_count):
    """
    Update a Grafana annotation to mark when new findings were uploaded.
    
    Args:
        findings_count: Number of findings uploaded
    
    Returns:
        dict: Response containing status code and message
    """
    # Only run if Grafana configuration is provided
    grafana_api_key = os.environ.get('GRAFANA_API_KEY')
    grafana_url = os.environ.get('GRAFANA_URL')
    
    if not grafana_api_key or not grafana_url:
        print("Grafana API key or URL not provided, skipping Grafana integration")
        return
    
    try:
        from grafana_client import GrafanaApi
        
        # Initialize Grafana client
        grafana = GrafanaApi.from_url(
            url=grafana_url,
            credential=grafana_api_key
        )
        
        # Create an annotation to mark the data update
        timestamp = int(time.time() * 1000)  # Convert to milliseconds
        annotation = {
            "dashboardId": 1,  # Replace with your actual dashboard ID
            "time": timestamp,
            "tags": ["findings-update", "automated"],
            "text": f"Security Hub findings updated: {findings_count} findings processed"
        }
        
        # Post the annotation
        response = grafana.annotations.add_annotation(annotation)
        print(f"Successfully added Grafana annotation: {response}")
        
    except Exception as e:
        print(f"Error updating Grafana dashboard: {str(e)}")
        # Non-critical, continue anyway
```

This is one of those small touches that dramatically improves the compliance user experience by showing exactly when control data was refreshed - a key consideration for audit evidence.

## Troubleshooting: Common Issues with Amazon Managed Grafana

When working with Amazon Managed Grafana for compliance dashboards, you may encounter these common issues:

### 1. Data Source Connection Issues
- **IAM permissions**: Verify that your Grafana workspace has the right permissions for Athena and S3. Check the service role attached to your Grafana workspace in the IAM console.
- **Region mismatch**: Ensure your Grafana data source is pointing to the same region as your compliance resources.
- **Resource names**: Double-check database, table, and S3 bucket names for typos or incorrect references.
- **VPC connectivity**: If your Grafana workspace is in a VPC, ensure proper network connectivity to your AWS resources.

### 2. "No Data" in Compliance Visualizations
- Check if your field names are lowercase (e.g., `severity` instead of `Severity`) - case sensitivity matters in SQL queries.
- Run your queries directly in Athena to verify they return compliance data.
- Check your variable references - they should use the format `${variable:sqlstring}` in your queries.
- Verify the time range selected in your dashboard is appropriate for your data.

### 3. Performance Issues
- Limit the amount of data you query by using effective WHERE clauses.
- Consider using aggregation queries instead of pulling all raw compliance data.
- If dashboard load times are slow, check which panels are taking the longest and optimize their queries.
- Use Athena workgroups with query result reuse to improve performance.

### 4. Authentication Problems
- For IAM Identity Center: Verify user assignments and roles in the IAM Identity Center console.
- For SAML: Check IdP configurations and attribute mappings in both your identity provider and Grafana workspace settings.
- Review the [Amazon Managed Grafana Authentication Troubleshooting guide](https://docs.aws.amazon.com/grafana/latest/userguide/troubleshooting-AMG-authentication.html) for specific solutions.

### 5. Plugin Installation Issues
- If you can't install or access the Athena plugin, verify your Grafana workspace has internet access.
- Check if your Grafana workspace version supports the plugin you're trying to install.
- Review the service access settings for your workspace to ensure it has permission to access the required AWS services.

For more troubleshooting assistance, refer to the [Amazon Managed Grafana Troubleshooting documentation](https://docs.aws.amazon.com/grafana/latest/userguide/troubleshooting-AMG.html).

## Your Next Steps as a GRC Professional

Once you've mastered the basics, try these techniques to level up your compliance visualization skills:

1. **Create Calculated Compliance Fields** in your queries for better risk analysis:
   ```sql
   SELECT 
     CASE 
       WHEN compliance_status = 'PASSED' THEN 'Compliant'
       WHEN compliance_status = 'WARNING' THEN 'At Risk'
       ELSE 'Non-Compliant' 
     END as compliance_category,
     COUNT(*) as finding_count
   FROM security_findings
   GROUP BY 1
   ```

2. **Build Compliance Trend Analysis** panels to show improvement over time:
   ```sql
   SELECT 
     date_trunc('day', from_iso8601_timestamp(found_at)) as finding_date,
     COUNT(*) as finding_count
   FROM security_findings
   GROUP BY 1
   ORDER BY 1
   ```

3. **Add Compliance Threshold Alerts** to notify your team when compliance drops below acceptable levels.

I've found that mastering these advanced techniques is what separates good GRC professionals from great ones. They enable you to go beyond reporting compliance data to actually driving meaningful improvements in your organization's security posture.

Feel free to reach out with questions as you build your compliance dashboard. We've all been beginners in GRC, and I'm here to help you grow into the compliance visualization expert your organization needs!

## Additional Resources

Here are essential resources for working with Amazon Managed Grafana for compliance dashboards:

- [Amazon Managed Grafana Documentation](https://docs.aws.amazon.com/grafana/latest/userguide/what-is-Amazon-Managed-Service-Grafana.html) - Official AWS documentation for Amazon Managed Grafana
- [Amazon Managed Grafana Workshop](https://catalog.workshops.aws/observability/en-US/amg) - Hands-on workshop for learning Amazon Managed Grafana
- [Grafana SQL Fundamentals](https://grafana.com/docs/grafana/latest/datasources/sql/) - Guide to working with SQL data sources in Grafana
- [Amazon Athena User Guide](https://docs.aws.amazon.com/athena/latest/ug/what-is.html) - Comprehensive guide to using Amazon Athena
- [AWS Security Hub User Guide](https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html) - Documentation for AWS Security Hub
- [Amazon Athena SQL Reference](https://docs.aws.amazon.com/athena/latest/ug/ddl-sql-reference.html) - Reference for Athena SQL commands and functions
- [Grafana Alerting Documentation](https://grafana.com/docs/grafana/latest/alerting/) - Guide to setting up alerts in Grafana
- [AWS Security Blog](https://aws.amazon.com/blogs/security/) - Blog posts about AWS security services and best practices 