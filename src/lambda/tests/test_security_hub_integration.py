import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock, mock_open

# Add the lambda directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import security_hub_integration

class TestSecurityHubIntegration(unittest.TestCase):
    """Tests for the Security Hub integration Lambda function"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Sample Security Hub findings
        self.mock_findings = [
            {
                'Id': 'arn:aws:securityhub:us-east-1:123456789012:finding/AC-2',
                'Title': 'AC.2 Account Management',
                'Description': ['Ensure proper account management procedures are implemented'],
                'Severity': {'Label': 'CRITICAL'},
                'Compliance': {'Status': 'FAILED'}
            },
            {
                'Id': 'arn:aws:securityhub:us-east-1:123456789012:finding/AC-3',
                'Title': 'AC.3 Access Enforcement',
                'Description': ['Implement access enforcement mechanisms'],
                'Severity': {'Label': 'HIGH'},
                'Compliance': {'Status': 'PASSED'}
            },
            {
                'Id': 'arn:aws:securityhub:us-east-1:123456789012:finding/SI-4',
                'Title': 'SI.4 Information System Monitoring',
                'Description': ['Monitor information system security alerts and advisories'],
                'Severity': {'Label': 'MEDIUM'},
                'Compliance': {'Status': 'NOT_APPLICABLE'}
            }
        ]
        
        # Set environment variables
        os.environ['BUCKET_NAME'] = 'test-bucket'
    
    def test_extract_family_from_title(self):
        """Test extraction of family from title"""
        finding = {'Title': 'AC.2 Account Management'}
        self.assertEqual(security_hub_integration.extract_family_from_title(finding), 'AC')
        
        finding = {'Title': 'No Family Format'}
        self.assertEqual(security_hub_integration.extract_family_from_title(finding), 'UNKNOWN')
    
    def test_extract_description(self):
        """Test extraction of description from finding"""
        finding = {'Description': ['Test description']}
        self.assertEqual(security_hub_integration.extract_description(finding), 'Test description')
        
        finding = {'Description': 'Single string description'}
        self.assertEqual(security_hub_integration.extract_description(finding), 'Single string description')
        
        finding = {}
        self.assertEqual(security_hub_integration.extract_description(finding), '')
    
    def test_get_status_from_compliance(self):
        """Test mapping of compliance status"""
        self.assertEqual(security_hub_integration.get_status_from_compliance('PASSED'), 'PASSED')
        self.assertEqual(security_hub_integration.get_status_from_compliance('FAILED'), 'FAILED')
        self.assertEqual(security_hub_integration.get_status_from_compliance('WARNING'), 'FAILED')
        self.assertEqual(security_hub_integration.get_status_from_compliance('NOT_APPLICABLE'), 'NOT_APPLICABLE')
        self.assertEqual(security_hub_integration.get_status_from_compliance('UNKNOWN_STATUS'), 'UNKNOWN')
    
    def test_process_findings(self):
        """Test processing of findings into datasets"""
        families_data, details_data = security_hub_integration.process_findings(self.mock_findings)
        
        # Check families data
        self.assertEqual(len(families_data), 2)  # AC and SI families
        
        # Find AC family data
        ac_family = next((f for f in families_data if f['family'] == 'AC'), None)
        self.assertIsNotNone(ac_family)
        self.assertEqual(ac_family['total'], 2)
        self.assertEqual(ac_family['passed'], 1)
        self.assertEqual(ac_family['failed'], 1)
        self.assertEqual(ac_family['compliance_percentage'], 50.0)
        
        # Check details data
        self.assertEqual(len(details_data), 3)
        self.assertEqual(details_data[0]['control_id'], 'AC-2')
        self.assertEqual(details_data[0]['status'], 'FAILED')
        self.assertEqual(details_data[1]['control_id'], 'AC-3')
        self.assertEqual(details_data[1]['status'], 'PASSED')
    
    @patch('security_hub_integration.get_security_hub_findings')
    @patch('security_hub_integration.upload_csv_to_s3')
    def test_lambda_handler(self, mock_upload, mock_get_findings):
        """Test the lambda handler function"""
        # Mock the findings
        mock_get_findings.return_value = self.mock_findings
        
        # Create event and context
        event = {}
        context = MagicMock()
        
        # Call the handler
        response = security_hub_integration.lambda_handler(event, context)
        
        # Check response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['families_count'], 2)
        self.assertEqual(body['controls_count'], 3)
        
        # Verify upload was called twice (once for each file)
        self.assertEqual(mock_upload.call_count, 2)

if __name__ == '__main__':
    unittest.main() 