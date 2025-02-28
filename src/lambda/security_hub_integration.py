import boto3
import csv
import json
import os
import logging
from datetime import datetime
from io import StringIO

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Main handler function for processing Security Hub findings and generating dashboard data
    """
    logger.info("Starting Security Hub data processing for cATO Dashboard")
    
    # Initialize clients
    securityhub = boto3.client('securityhub')
    s3 = boto3.client('s3')
    
    # Get configuration from environment variables
    bucket_name = os.environ['BUCKET_NAME']
    control_families_key = os.environ.get('CONTROL_FAMILIES_KEY', 'controls/control_families.csv')
    control_details_key = os.environ.get('CONTROL_DETAILS_KEY', 'controls/control_details.csv')
    
    try:
        # Get Security Hub findings
        logger.info("Retrieving Security Hub findings")
        findings = get_security_hub_findings(securityhub)
        logger.info(f"Retrieved {len(findings)} findings from Security Hub")
        
        # Process findings into our CSV format
        logger.info("Processing findings into dashboard data format")
        families_data, details_data = process_findings(findings)
        
        # Upload to S3
        logger.info(f"Uploading data to S3 bucket {bucket_name}")
        upload_csv_to_s3(s3, families_data, bucket_name, control_families_key)
        upload_csv_to_s3(s3, details_data, bucket_name, control_details_key)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully updated cATO dashboard data',
                'timestamp': datetime.now().isoformat(),
                'families_count': len(families_data),
                'controls_count': len(details_data)
            })
        }
    
    except Exception as e:
        logger.error(f"Error processing Security Hub data: {str(e)}")
        raise

def get_security_hub_findings(client):
    """
    Retrieve all active findings from Security Hub
    """
    findings = []
    paginator = client.get_paginator('get_findings')
    
    # Filter for NIST findings and active records
    filters = {
        'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}],
        'ComplianceStandards': [{'Value': 'NIST', 'Comparison': 'CONTAINS'}]
    }
    
    try:
        for page in paginator.paginate(Filters=filters):
            findings.extend(page['Findings'])
        return findings
    except Exception as e:
        logger.error(f"Error retrieving findings: {str(e)}")
        raise

def process_findings(findings):
    """
    Process findings into two datasets:
    1. Control families summary (family level statistics)
    2. Detailed control information
    """
    # Initialize data structures
    families = {}
    details = []
    
    # Process each finding
    for finding in findings:
        # Extract family from the control ID (e.g., AC-1 -> AC)
        control_id = finding.get('Id', '').split('/')[-1]
        family = control_id.split('-')[0] if '-' in control_id else extract_family_from_title(finding)
        
        # Get status and severity
        status = get_status_from_compliance(finding.get('Compliance', {}).get('Status'))
        severity = finding.get('Severity', {}).get('Label', 'UNKNOWN')
        
        # Update families statistics
        if family not in families:
            families[family] = {'total': 0, 'passed': 0, 'failed': 0, 
                              'not_applicable': 0, 'unknown': 0}
        
        families[family]['total'] += 1
        status_key = status.lower()
        if status_key in families[family]:
            families[family][status_key] += 1
        
        # Add to details
        details.append({
            'control_id': control_id,
            'family': family,
            'status': status,
            'severity': severity,
            'description': extract_description(finding)
        })
    
    # Calculate compliance percentages and format families data
    families_data = []
    for family, stats in families.items():
        total_applicable = stats['total'] - stats.get('not_applicable', 0)
        compliance_percentage = (stats['passed'] / total_applicable * 100) if total_applicable > 0 else 0
        families_data.append({
            'family': family,
            'total': stats['total'],
            'passed': stats['passed'],
            'failed': stats['failed'],
            'not_applicable': stats.get('not_applicable', 0),
            'unknown': stats.get('unknown', 0),
            'compliance_percentage': round(compliance_percentage, 2)
        })
    
    return families_data, details

def extract_family_from_title(finding):
    """Extract control family from finding title if not present in ID"""
    title = finding.get('Title', '')
    if '.' in title:
        return title.split('.')[0]
    return 'UNKNOWN'

def extract_description(finding):
    """Extract description from finding"""
    description = finding.get('Description', '')
    if isinstance(description, list) and len(description) > 0:
        return description[0]
    return str(description)

def get_status_from_compliance(status):
    """Map Security Hub compliance status to our status format"""
    status_map = {
        'PASSED': 'PASSED',
        'FAILED': 'FAILED',
        'WARNING': 'FAILED',
        'NOT_AVAILABLE': 'UNKNOWN',
        'NOT_APPLICABLE': 'NOT_APPLICABLE'
    }
    return status_map.get(status, 'UNKNOWN')

def upload_csv_to_s3(client, data, bucket, key):
    """
    Convert data to CSV format and upload to S3
    """
    if not data:
        logger.warning(f"No data to upload for {key}")
        return
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    
    # Upload to S3
    try:
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=output.getvalue(),
            ContentType='text/csv'
        )
        logger.info(f"Successfully uploaded {key} to S3")
    except Exception as e:
        logger.error(f"Error uploading to S3: {str(e)}")
        raise 