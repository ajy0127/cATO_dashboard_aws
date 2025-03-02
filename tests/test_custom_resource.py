import json
import os
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add the src directory to the path so we can import the lambda function
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)
import lambda_function


class TestCustomResourceHandling(unittest.TestCase):
    @patch("lambda_function.send_cloudformation_response")
    @patch("lambda_function.process_findings")
    def test_create_request(self, mock_process_findings, mock_send_response):
        # Setup mocks
        mock_process_findings.return_value = {
            "statusCode": 200,
            "body": "Successfully processed findings",
        }
        mock_send_response.return_value = 200

        # Create a mock event for a CloudFormation Create request
        event = {
            "RequestType": "Create",
            "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/response",
            "StackId": "arn:aws:cloudformation:us-east-1:123456789012:stack/stack-name/guid",
            "RequestId": "unique id for this create request",
            "ResourceType": "Custom::LambdaInvoke",
            "LogicalResourceId": "InitialLambdaInvocation",
            "ResourceProperties": {
                "ServiceToken": "arn:aws:lambda:us-east-1:123456789012:function:lambda-name",
                "Version": "1.0",
            },
        }

        # Create a mock context
        context = MagicMock()
        context.log_stream_name = "log-stream-name"

        # Call the Lambda handler
        lambda_function.lambda_handler(event, context)

        # Verify process_findings was called
        mock_process_findings.assert_called_once()

        # Verify send_cloudformation_response was called with the correct parameters
        mock_send_response.assert_called_once()
        args, kwargs = mock_send_response.call_args
        self.assertEqual(args[0], event)
        self.assertEqual(args[1], context)
        self.assertEqual(args[2], "SUCCESS")
        self.assertEqual(args[3], {"Message": "Successfully processed findings"})

    @patch("lambda_function.send_cloudformation_response")
    @patch("lambda_function.process_findings")
    def test_delete_request(self, mock_process_findings, mock_send_response):
        # Setup mock
        mock_send_response.return_value = 200

        # Create a mock event for a CloudFormation Delete request
        event = {
            "RequestType": "Delete",
            "ResponseURL": "https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/response",
            "StackId": "arn:aws:cloudformation:us-east-1:123456789012:stack/stack-name/guid",
            "RequestId": "unique id for this delete request",
            "ResourceType": "Custom::LambdaInvoke",
            "LogicalResourceId": "InitialLambdaInvocation",
        }

        # Create a mock context
        context = MagicMock()
        context.log_stream_name = "log-stream-name"

        # Call the Lambda handler
        lambda_function.lambda_handler(event, context)

        # Verify process_findings was NOT called (for Delete requests)
        mock_process_findings.assert_not_called()

        # Verify send_cloudformation_response was called with the correct parameters
        mock_send_response.assert_called_once()
        args, kwargs = mock_send_response.call_args
        self.assertEqual(args[0], event)
        self.assertEqual(args[1], context)
        self.assertEqual(args[2], "SUCCESS")
        self.assertEqual(args[3], {})

    @patch("lambda_function.process_findings")
    def test_regular_invocation(self, mock_process_findings):
        # Setup mock
        mock_process_findings.return_value = {
            "statusCode": 200,
            "body": "Successfully processed findings",
        }

        # Create a normal event (not a CloudFormation request)
        event = {}
        context = {}

        # Call the Lambda handler
        result = lambda_function.lambda_handler(event, context)

        # Verify process_findings was called
        mock_process_findings.assert_called_once()

        # Verify the result
        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(result["body"], json.dumps("Successfully processed findings"))


if __name__ == "__main__":
    unittest.main()
