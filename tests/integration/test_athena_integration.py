import os
import sys
import unittest
import boto3
import time
from unittest.mock import patch

# Add the src directory to the path so we can import the lambda function
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

# Import the lambda function
import lambda_function


class TestAthenaIntegration(unittest.TestCase):
    """Integration tests for Athena functionality.

    Note: These tests require AWS credentials and will create actual resources.
    They should be run in a test environment, not production.
    """

    @classmethod
    def setUpClass(cls):
        """Set up test resources."""
        # Create a test S3 bucket for findings
        cls.s3_client = boto3.client("s3")
        cls.bucket_name = f"cato-test-bucket-{int(time.time())}"
        cls.s3_client.create_bucket(Bucket=cls.bucket_name)

        # Set environment variables
        os.environ["FINDINGS_BUCKET"] = cls.bucket_name
        os.environ["ATHENA_DATABASE"] = "cato_test_db"
        os.environ["ATHENA_TABLE"] = "security_findings_test"
        os.environ["ATHENA_WORKGROUP"] = "primary"

        # Create Athena client
        cls.athena_client = boto3.client("athena")

        # Create test database
        cls.athena_client.start_query_execution(
            QueryString=f"CREATE DATABASE IF NOT EXISTS {os.environ['ATHENA_DATABASE']}",
            ResultConfiguration={
                "OutputLocation": f"s3://{cls.bucket_name}/athena-results/"
            },
        )

        # Wait for database creation to complete
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        """Clean up test resources."""
        # Delete all objects in the bucket
        response = cls.s3_client.list_objects_v2(Bucket=cls.bucket_name)
        if "Contents" in response:
            for obj in response["Contents"]:
                cls.s3_client.delete_object(Bucket=cls.bucket_name, Key=obj["Key"])

        # Delete the bucket
        cls.s3_client.delete_bucket(Bucket=cls.bucket_name)

        # Drop the test database
        cls.athena_client.start_query_execution(
            QueryString=f"DROP DATABASE IF EXISTS {os.environ['ATHENA_DATABASE']} CASCADE",
            ResultConfiguration={
                "OutputLocation": f"s3://{cls.bucket_name}/athena-results/"
            },
        )

    @patch("lambda_function.get_security_hub_findings")
    def test_athena_table_creation(self, mock_get_findings):
        """Test that the Athena table is created correctly."""
        # Mock the findings
        mock_get_findings.return_value = [
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

        # Call the lambda handler
        lambda_function.lambda_handler({}, {})

        # Verify the table was created
        response = self.athena_client.start_query_execution(
            QueryString=f"SELECT * FROM {os.environ['ATHENA_DATABASE']}.{os.environ['ATHENA_TABLE']} LIMIT 10",
            ResultConfiguration={
                "OutputLocation": f"s3://{cls.bucket_name}/athena-results/"
            },
        )

        # Get the query execution ID
        query_execution_id = response["QueryExecutionId"]

        # Wait for the query to complete
        status = "RUNNING"
        while status in ["RUNNING", "QUEUED"]:
            time.sleep(1)
            response = self.athena_client.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            status = response["QueryExecution"]["Status"]["State"]

        # Check if the query was successful
        self.assertEqual(status, "SUCCEEDED")

        # Get the query results
        response = self.athena_client.get_query_results(
            QueryExecutionId=query_execution_id
        )

        # Verify the results
        self.assertTrue(len(response["ResultSet"]["Rows"]) > 1)  # Header row + data row


if __name__ == "__main__":
    unittest.main()
