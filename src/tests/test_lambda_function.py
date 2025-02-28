import json
import os
import unittest
from unittest.mock import patch, MagicMock
import boto3
import sys

# Add the parent directory to the path so we can import the lambda function
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lambda_function

class TestLambdaFunction(unittest.TestCase):
    @patch('lambda_function.boto3.client')
    @patch('lambda_function.datetime')
    def test_lambda_handler_success(self, mock_datetime, mock_boto):
        # Mock datetime to return a fixed timestamp
        mock_datetime.datetime.now.return_value.strftime.return_value = '20250101-120000'
        
        # Set up environment variable
        os.environ['BUCKET_NAME'] = 'test-bucket'
        
        # Mock Security Hub and S3 clients
        mock_securityhub = MagicMock()
        mock_s3 = MagicMock()
        
        # Configure mock clients to be returned by boto3.client
        def mock_client(service, *args, **kwargs):
            if service == 'securityhub':
                return mock_securityhub
            elif service == 's3':
                return mock_s3
            else:
                raise ValueError(f"Unexpected service: {service}")
        
        mock_boto.side_effect = mock_client
        
        # Configure mock Security Hub response
        mock_securityhub.get_findings.return_value = {
            'Findings': [
                {
                    'Id': 'test-finding-1',
                    'Title': 'Test Finding 1',
                    'Description': 'This is a test finding',
                    'Severity': {'Label': 'HIGH'},
                    'Resources': [{'Type': 'AwsEc2Instance', 'Id': 'i-12345'}],
                    'CreatedAt': '2025-01-01T12:00:00Z',
                    'Workflow': {'Status': 'NEW'},
                    'Compliance': {'Status': 'FAILED'},
                    'ProductName': 'Security Hub',
                    'CompanyName': 'AWS',
                    'Region': 'us-east-1'
                }
            ]
        }
        
        # Call the lambda handler
        response = lambda_function.lambda_handler({}, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Successfully uploaded', response['body'])
        
        # Verify S3 put_object was called with correct parameters
        mock_s3.put_object.assert_called_once()
        call_args = mock_s3.put_object.call_args[1]
        self.assertEqual(call_args['Bucket'], 'test-bucket')
        self.assertEqual(call_args['Key'], 'security-hub-findings-20250101-120000.json')
        self.assertEqual(call_args['ContentType'], 'application/json')
        
        # Verify the content of the uploaded JSON
        uploaded_content = json.loads(call_args['Body'])
        self.assertEqual(len(uploaded_content), 1)
        self.assertEqual(uploaded_content[0]['id'], 'test-finding-1')
        self.assertEqual(uploaded_content[0]['severity'], 'HIGH')

    @patch('lambda_function.boto3.client')
    def test_lambda_handler_no_bucket(self, mock_boto):
        # Clear environment variable
        if 'BUCKET_NAME' in os.environ:
            del os.environ['BUCKET_NAME']
        
        # Call the lambda handler
        response = lambda_function.lambda_handler({}, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('BUCKET_NAME environment variable not set', response['body'])

    @patch('lambda_function.boto3.client')
    def test_lambda_handler_no_findings(self, mock_boto):
        # Set up environment variable
        os.environ['BUCKET_NAME'] = 'test-bucket'
        
        # Mock Security Hub and S3 clients
        mock_securityhub = MagicMock()
        mock_s3 = MagicMock()
        
        # Configure mock clients to be returned by boto3.client
        def mock_client(service, *args, **kwargs):
            if service == 'securityhub':
                return mock_securityhub
            elif service == 's3':
                return mock_s3
            else:
                raise ValueError(f"Unexpected service: {service}")
        
        mock_boto.side_effect = mock_client
        
        # Configure mock Security Hub response with no findings
        mock_securityhub.get_findings.return_value = {
            'Findings': []
        }
        
        # Call the lambda handler
        response = lambda_function.lambda_handler({}, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('No active findings found', response['body'])
        
        # Verify S3 put_object was not called
        mock_s3.put_object.assert_not_called()

if __name__ == '__main__':
    unittest.main() 