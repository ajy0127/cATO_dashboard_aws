import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path so we can import the lambda function
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

# Import the lambda function
import lambda_function


class TestLambdaFunction(unittest.TestCase):
    """Test cases for the lambda_function.py file."""

    @patch("lambda_function.boto3.client")
    def test_get_security_hub_findings(self, mock_client):
        """Test the get_security_hub_findings function."""
        # Setup mock response
        mock_security_hub = MagicMock()
        mock_client.return_value = mock_security_hub

        mock_response = {
            "Findings": [
                {
                    "Id": "test-finding-1",
                    "ProductName": "Security Hub",
                    "Title": "Test Finding 1",
                    "Description": "This is a test finding",
                    "Severity": {"Label": "HIGH"},
                    "Compliance": {"Status": "FAILED"},
                    "CreatedAt": "2023-01-01T00:00:00.000Z",
                }
            ],
            "NextToken": None,
        }
        mock_security_hub.get_findings.return_value = mock_response

        # Call the function
        findings = lambda_function.get_security_hub_findings()

        # Assertions
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["Id"], "test-finding-1")
        self.assertEqual(findings[0]["ProductName"], "Security Hub")
        self.assertEqual(findings[0]["Severity"], "HIGH")
        self.assertEqual(findings[0]["Status"], "FAILED")

        # Verify the correct parameters were passed to get_findings
        mock_security_hub.get_findings.assert_called_once()

    @patch("lambda_function.boto3.client")
    def test_save_findings_to_s3(self, mock_client):
        """Test the save_findings_to_s3 function."""
        # Setup mock response
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3

        # Test data
        findings = [
            {
                "Id": "test-finding-1",
                "ProductName": "Security Hub",
                "Title": "Test Finding 1",
                "Description": "This is a test finding",
                "Severity": "HIGH",
                "Status": "FAILED",
                "CreatedAt": "2023-01-01T00:00:00.000Z",
            }
        ]

        # Mock environment variables
        with patch.dict(os.environ, {"FINDINGS_BUCKET": "test-bucket"}):
            # Call the function
            lambda_function.save_findings_to_s3(findings)

            # Assertions
            mock_s3.put_object.assert_called_once()
            args, kwargs = mock_s3.put_object.call_args
            self.assertEqual(kwargs["Bucket"], "test-bucket")
            self.assertTrue("findings_" in kwargs["Key"])
            self.assertTrue(isinstance(kwargs["Body"], str))

    def test_lambda_handler(self):
        """Test the lambda_handler function."""
        # This is a more complex test that would require mocking multiple functions
        # For now, we'll just test that it doesn't raise exceptions
        with patch(
            "lambda_function.get_security_hub_findings"
        ) as mock_get_findings, patch(
            "lambda_function.save_findings_to_s3"
        ) as mock_save_to_s3, patch(
            "lambda_function.update_athena_table"
        ) as mock_update_athena:

            mock_get_findings.return_value = []

            # Call the handler
            result = lambda_function.lambda_handler({}, {})

            # Assertions
            self.assertEqual(result["statusCode"], 200)
            mock_get_findings.assert_called_once()
            mock_save_to_s3.assert_called_once_with([])
            mock_update_athena.assert_called_once()


if __name__ == "__main__":
    unittest.main()
