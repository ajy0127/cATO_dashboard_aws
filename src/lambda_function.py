import json
import boto3
import requests
import os
import datetime
import urllib.request

def process_findings():
    """
    Process Security Hub findings and store them in S3.
    
    Returns:
        dict: Response containing status code and message
    """
    # Get bucket name from environment variable
    s3_bucket = os.environ.get('BUCKET_NAME')
    
    if not s3_bucket:
        return {
            'statusCode': 500,
            'body': 'Error: BUCKET_NAME environment variable not set'
        }
    
    try:
        # Initialize clients
        security_hub = boto3.client('securityhub')
        s3 = boto3.client('s3')
        
        # Get findings from Security Hub
        response = security_hub.get_findings(
            MaxResults=100,  # Adjust based on your needs
            Filters={
                'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
            }
        )
        
        findings = response.get('Findings', [])
        
        if not findings:
            return {
                'statusCode': 200,
                'body': 'No active findings found in Security Hub'
            }
        
        # Process findings for cATO Dashboard format
        processed_findings = []
        
        for finding in findings:
            processed_finding = {
                'id': finding.get('Id'),
                'title': finding.get('Title'),
                'description': finding.get('Description'),
                'severity': finding.get('Severity', {}).get('Label', 'UNKNOWN'),
                'resource_type': finding.get('Resources', [{}])[0].get('Type') if finding.get('Resources') else 'Unknown',
                'resource_id': finding.get('Resources', [{}])[0].get('Id') if finding.get('Resources') else 'Unknown',
                'found_at': finding.get('CreatedAt'),
                'status': finding.get('Workflow', {}).get('Status', 'NEW'),
                'compliance_status': finding.get('Compliance', {}).get('Status', 'UNKNOWN'),
                'product_name': finding.get('ProductName'),
                'company_name': finding.get('CompanyName'),
                'region': finding.get('Region', 'unknown')
            }
            
            processed_findings.append(processed_finding)
        
        # Create a timestamped filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f'security-hub-findings-{timestamp}.json'
        
        # Upload to S3
        s3.put_object(
            Bucket=s3_bucket,
            Key=filename,
            Body=json.dumps(processed_findings, indent=2),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200,
            'body': f'Successfully uploaded {len(processed_findings)} findings to S3 bucket {s3_bucket}'
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }

def send_cloudformation_response(event, context, response_status, response_data, physical_resource_id=None):
    """
    Send a response to CloudFormation for a custom resource request.
    
    Args:
        event (dict): The CloudFormation custom resource event
        context (object): The Lambda context
        response_status (str): 'SUCCESS' or 'FAILED'
        response_data (dict): The data to send back to CloudFormation
        physical_resource_id (str, optional): The physical resource ID. Defaults to None.
    """
    response_url = event.get('ResponseURL')
    
    if not response_url:
        print("No ResponseURL found in the event")
        return
    
    response_body = {
        'Status': response_status,
        'Reason': f'See details in CloudWatch Log Stream: {context.log_stream_name}',
        'PhysicalResourceId': physical_resource_id or context.log_stream_name,
        'StackId': event.get('StackId'),
        'RequestId': event.get('RequestId'),
        'LogicalResourceId': event.get('LogicalResourceId'),
        'Data': response_data
    }
    
    print(f"Sending response to CloudFormation: {json.dumps(response_body)}")
    
    req = urllib.request.Request(
        url=response_url,
        data=json.dumps(response_body).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"CloudFormation response status: {response.status}")
            return response.status
    except Exception as e:
        print(f"Failed to send response to CloudFormation: {str(e)}")
        return None

def lambda_handler(event, context):
    """
    AWS Lambda function to retrieve findings from Security Hub and store them in S3.
    
    This function:
    1. Handles CloudFormation custom resource requests
    2. Queries AWS Security Hub for all findings
    3. Transforms the data as needed for cATO Dashboard
    4. Uploads the findings to the S3 bucket
    
    Args:
        event (dict): The Lambda event
        context (object): The Lambda context
        
    Returns:
        dict: Response containing status code and message
    """
    # Check if this is a CloudFormation custom resource request
    if event.get('RequestType') in ['Create', 'Update', 'Delete']:
        print(f"Processing CloudFormation {event['RequestType']} request")
        
        # For Delete requests, just send success response
        if event['RequestType'] == 'Delete':
            return send_cloudformation_response(event, context, 'SUCCESS', {})
        
        # For Create/Update, process findings and send response
        try:
            result = process_findings()
            response_data = {'Message': result['body']}
            response_status = 'SUCCESS' if result['statusCode'] == 200 else 'FAILED'
            return send_cloudformation_response(event, context, response_status, response_data)
        except Exception as e:
            print(f"Error processing CloudFormation request: {str(e)}")
            return send_cloudformation_response(event, context, 'FAILED', {'Error': str(e)})
    
    # For regular Lambda invocations
    result = process_findings()
    # Format response as expected by API Gateway or direct invocation
    return {
        'statusCode': result['statusCode'],
        'body': json.dumps(result['body'])
    } 