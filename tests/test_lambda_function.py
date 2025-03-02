import json
import os
import unittest
from unittest.mock import patch, MagicMock
import boto3
import sys

# Add the src directory to the path so we can import the lambda function
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)
import lambda_function


class TestLambdaFunction(unittest.TestCase):
    @patch("lambda_function.boto3.client")
    @patch("lambda_function.datetime")
    def test_lambda_handler_success(self, mock_datetime, mock_boto):
        # Mock datetime to return a fixed timestamp
        mock_datetime.datetime.now.return_value.strftime.return_value = (
            "20250101-120000"
        )

        # Set up environment variables
        os.environ["S3_BUCKET_NAME"] = "test-bucket"
        os.environ["ATHENA_RESULTS_BUCKET"] = "test-athena-bucket"

        # Mock Security Hub and S3 clients
        mock_securityhub = MagicMock()
        mock_s3 = MagicMock()
        mock_athena = MagicMock()
        mock_glue = MagicMock()

        # Configure mock clients to be returned by boto3.client
        def mock_client(service, *args, **kwargs):
            if service == "securityhub":
                return mock_securityhub
            elif service == "s3":
                return mock_s3
            elif service == "athena":
                return mock_athena
            elif service == "glue":
                return mock_glue
            else:
                raise ValueError(f"Unexpected service: {service}")

        mock_boto.side_effect = mock_client

        # Configure mock Security Hub response
        mock_securityhub.get_findings.return_value = {
            "Findings": [
                {
                    "Id": "test-finding-1",
                    "Title": "Test Finding 1",
                    "Description": "This is a test finding",
                    "Severity": {"Label": "HIGH"},
                    "Resources": [{"Type": "AwsEc2Instance", "Id": "i-12345"}],
                    "CreatedAt": "2025-01-01T12:00:00Z",
                    "Workflow": {"Status": "NEW"},
                    "Compliance": {"Status": "FAILED"},
                    "ProductName": "Security Hub",
                    "CompanyName": "AWS",
                    "Region": "us-east-1",
                }
            ]
        }

        # Call the lambda handler
        response = lambda_function.lambda_handler({}, {})

        # Verify the response
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Successfully uploaded", response["body"])

        # Verify S3 put_object was called with correct parameters
        mock_s3.put_object.assert_called_once()
        call_args = mock_s3.put_object.call_args[1]
        self.assertEqual(call_args["Bucket"], "test-bucket")
        self.assertEqual(call_args["Key"], "security-hub-findings-20250101-120000.json")
        self.assertEqual(call_args["ContentType"], "application/json")

        # Verify some content was uploaded
        uploaded_content = json.loads(call_args["Body"])
        # Check if it's a list or a dictionary (depending on the implementation)
        if isinstance(uploaded_content, list):
            # List implementation
            self.assertGreater(len(uploaded_content), 0)
            # Verify at least one item has our test finding ID
            found = False
            for item in uploaded_content:
                if "id" in item and item["id"] == "test-finding-1":
                    found = True
                    break
            self.assertTrue(found, "Test finding ID not found in uploaded content")
        else:
            # Dictionary implementation
            self.assertIsInstance(uploaded_content, dict)
            self.assertEqual(uploaded_content.get("id"), "test-finding-1")
            self.assertEqual(uploaded_content.get("severity"), "HIGH")

    @patch("lambda_function.boto3.client")
    def test_lambda_handler_no_bucket(self, mock_boto):
        # Clear environment variables
        if "S3_BUCKET_NAME" in os.environ:
            del os.environ["S3_BUCKET_NAME"]

        # Ensure ATHENA_RESULTS_BUCKET is set to avoid that error
        os.environ["ATHENA_RESULTS_BUCKET"] = "test-athena-bucket"

        # Call the lambda handler
        response = lambda_function.lambda_handler({}, {})

        # Verify the response
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("S3_BUCKET_NAME environment variable not set", response["body"])

    @patch("lambda_function.boto3.client")
    def test_lambda_handler_no_findings(self, mock_boto):
        # Set up environment variables
        os.environ["S3_BUCKET_NAME"] = "test-bucket"
        os.environ["ATHENA_RESULTS_BUCKET"] = "test-athena-bucket"

        # Mock Security Hub and S3 clients
        mock_securityhub = MagicMock()
        mock_s3 = MagicMock()
        mock_athena = MagicMock()
        mock_glue = MagicMock()

        # Configure mock clients to be returned by boto3.client
        def mock_client(service, *args, **kwargs):
            if service == "securityhub":
                return mock_securityhub
            elif service == "s3":
                return mock_s3
            elif service == "athena":
                return mock_athena
            elif service == "glue":
                return mock_glue
            else:
                raise ValueError(f"Unexpected service: {service}")

        mock_boto.side_effect = mock_client

        # Configure mock Security Hub response with no findings
        mock_securityhub.get_findings.return_value = {"Findings": []}

        # Call the lambda handler
        response = lambda_function.lambda_handler({}, {})

        # Verify the response
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("No active findings found", response["body"])

        # The Lambda now creates an empty file even when there are no findings,
        # so we check that put_object is called with an empty string
        mock_s3.put_object.assert_called_once()
        call_args = mock_s3.put_object.call_args[1]
        self.assertEqual(call_args["Body"], "")


if __name__ == "__main__":
    unittest.main()
