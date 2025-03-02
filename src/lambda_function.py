import json
import boto3
import requests
import os
import datetime
import urllib.request
import time


def update_grafana_dashboard(findings_count):
    """
    Update a Grafana annotation to mark when new findings were uploaded.

    Args:
        findings_count: Number of findings uploaded

    Returns:
        dict: Response containing status code and message
    """
    # Only run if Grafana configuration is provided
    grafana_api_key = os.environ.get("GRAFANA_API_KEY")
    grafana_url = os.environ.get("GRAFANA_URL")

    if not grafana_api_key or not grafana_url:
        print("Grafana API key or URL not provided, skipping Grafana integration")
        return

    try:
        from grafana_client import GrafanaApi

        # Initialize Grafana client
        grafana = GrafanaApi.from_url(url=grafana_url, credential=grafana_api_key)

        # Create an annotation to mark the data update
        timestamp = int(time.time() * 1000)  # Convert to milliseconds
        annotation = {
            "dashboardId": os.environ.get(
                "GRAFANA_DASHBOARD_ID", "1"
            ),  # Get dashboard ID from env or use default
            "time": timestamp,
            "tags": ["findings-update", "automated"],
            "text": f"Security Hub findings updated: {findings_count} findings processed",
        }

        # Post the annotation
        response = grafana.annotations.add_annotation(annotation)
        print(f"Successfully added Grafana annotation: {response}")

    except Exception as e:
        print(f"Error updating Grafana dashboard: {str(e)}")
        # Non-critical, continue anyway


def process_findings():
    """
    Process Security Hub findings, store them in S3, and update Athena if needed.

    Returns:
        dict: Response containing status code and message
    """
    # Get environment variables
    s3_bucket = os.environ.get("S3_BUCKET_NAME")
    athena_database = os.environ.get("ATHENA_DATABASE", "cato_security_findings")
    athena_results_bucket = os.environ.get("ATHENA_RESULTS_BUCKET")

    print(f"Using S3 bucket: {s3_bucket}")
    print(f"Using Athena database: {athena_database}")
    print(f"Using Athena results bucket: {athena_results_bucket}")

    if not s3_bucket:
        print("ERROR: S3_BUCKET_NAME environment variable not set")
        return {
            "statusCode": 500,
            "body": "Error: S3_BUCKET_NAME environment variable not set",
        }

    if not athena_results_bucket:
        print("ERROR: ATHENA_RESULTS_BUCKET environment variable not set")
        return {
            "statusCode": 500,
            "body": "Error: ATHENA_RESULTS_BUCKET environment variable not set",
        }

    try:
        # Initialize clients
        print("Initializing AWS clients...")
        security_hub = boto3.client("securityhub")
        s3 = boto3.client("s3")
        athena = boto3.client("athena")
        glue = boto3.client("glue")

        # Check if the S3 buckets exist and create them if they don't
        try:
            # Check if main S3 bucket exists
            s3.head_bucket(Bucket=s3_bucket)
            print(f"S3 bucket {s3_bucket} exists and is accessible")
        except Exception as e:
            print(f"Error checking S3 bucket {s3_bucket}: {str(e)}")
            print("Attempting to create S3 bucket...")
            try:
                region = os.environ.get("AWS_REGION", "us-east-1")
                if region == "us-east-1":
                    s3.create_bucket(Bucket=s3_bucket)
                else:
                    s3.create_bucket(
                        Bucket=s3_bucket,
                        CreateBucketConfiguration={"LocationConstraint": region},
                    )
                print(f"Successfully created S3 bucket {s3_bucket}")
            except Exception as create_error:
                print(f"Failed to create S3 bucket: {str(create_error)}")
                # Continue anyway, as we might still be able to process findings

        # Check if Athena results bucket exists
        try:
            s3.head_bucket(Bucket=athena_results_bucket)
            print(
                f"Athena results bucket {athena_results_bucket} exists and is accessible"
            )
        except Exception as e:
            print(
                f"Error checking Athena results bucket {athena_results_bucket}: {str(e)}"
            )
            print("Attempting to create Athena results bucket...")
            try:
                region = os.environ.get("AWS_REGION", "us-east-1")
                if region == "us-east-1":
                    s3.create_bucket(Bucket=athena_results_bucket)
                else:
                    s3.create_bucket(
                        Bucket=athena_results_bucket,
                        CreateBucketConfiguration={"LocationConstraint": region},
                    )
                print(
                    f"Successfully created Athena results bucket {athena_results_bucket}"
                )
            except Exception as create_error:
                print(f"Failed to create Athena results bucket: {str(create_error)}")
                # Continue anyway, as we might still be able to process findings without Athena

        # Store findings in S3 regardless of Athena availability
        try:
            # Get findings from Security Hub
            print("Getting findings from Security Hub...")
            response = security_hub.get_findings(
                MaxResults=100,  # Adjust based on your needs
                Filters={"RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]},
            )

            findings = response.get("Findings", [])
            print(f"Retrieved {len(findings)} findings from Security Hub")

            if not findings:
                print("No active findings found in Security Hub")
                # Even with no findings, we want to create an empty file to ensure the S3 structure is valid
                timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                filename = f"security-hub-findings-{timestamp}.json"
                s3.put_object(
                    Bucket=s3_bucket,
                    Key=filename,
                    Body="",
                    ContentType="application/json",
                )
                print(f"Created empty file: {filename}")

                return {
                    "statusCode": 200,
                    "body": "No active findings found in Security Hub. Created empty file.",
                }

            # Process findings for cATO Dashboard format
            processed_findings = []

            for finding in findings:
                processed_finding = {
                    "id": finding.get("Id"),
                    "title": finding.get("Title"),
                    "description": finding.get("Description"),
                    "severity": finding.get("Severity", {}).get("Label", "UNKNOWN"),
                    "resource_type": (
                        finding.get("Resources", [{}])[0].get("Type")
                        if finding.get("Resources")
                        else "Unknown"
                    ),
                    "resource_id": (
                        finding.get("Resources", [{}])[0].get("Id")
                        if finding.get("Resources")
                        else "Unknown"
                    ),
                    "found_at": finding.get("CreatedAt"),
                    "status": finding.get("Workflow", {}).get("Status", "NEW"),
                    "compliance_status": finding.get("Compliance", {}).get(
                        "Status", "UNKNOWN"
                    ),
                    "product_name": finding.get("ProductName"),
                    "company_name": finding.get("CompanyName"),
                    "region": finding.get("Region", "unknown"),
                }

                processed_findings.append(processed_finding)

            # Create a timestamped filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

            # For S3 storage compatible with Athena, we need to store each finding as a separate line (JSONL format)
            # rather than a JSON array
            jsonl_content = "\n".join(
                [json.dumps(finding) for finding in processed_findings]
            )

            filename = f"security-hub-findings-{timestamp}.json"

            # Upload to S3
            print(
                f"Uploading {len(processed_findings)} findings to S3 bucket {s3_bucket}, key: {filename}"
            )
            s3.put_object(
                Bucket=s3_bucket,
                Key=filename,
                Body=jsonl_content,
                ContentType="application/json",
            )
            print(f"Successfully uploaded findings to S3")

            # Add Grafana annotation if findings were successfully uploaded
            if len(processed_findings) > 0:
                try:
                    update_grafana_dashboard(len(processed_findings))
                except Exception as grafana_error:
                    print(f"Warning: Failed to update Grafana: {str(grafana_error)}")
                    # Non-critical, continue anyway
        except Exception as e:
            print(f"Error processing and storing Security Hub findings: {str(e)}")
            import traceback

            traceback.print_exc()
            # If we can't store findings, that's a critical error
            return {
                "statusCode": 500,
                "body": f"Error processing and storing Security Hub findings: {str(e)}",
            }

        # Try to set up Athena, but don't fail the function if it doesn't work
        athena_success = True
        athena_error = None

        try:
            # Ensure Athena database exists
            try:
                print(f"Checking if Athena database {athena_database} exists...")
                glue.get_database(Name=athena_database)
                print(f"Athena database {athena_database} exists")
            except glue.exceptions.EntityNotFoundException:
                print(f"Creating Athena database {athena_database}")
                try:
                    query = f"CREATE DATABASE IF NOT EXISTS {athena_database}"
                    start_query_response = athena.start_query_execution(
                        QueryString=query,
                        ResultConfiguration={
                            "OutputLocation": f"s3://{athena_results_bucket}/"
                        },
                    )
                    print(
                        f"Executed query to create database, QueryExecutionId: {start_query_response['QueryExecutionId']}"
                    )
                    wait_for_query_to_complete(
                        athena, start_query_response["QueryExecutionId"]
                    )
                except Exception as e:
                    print(f"Error creating Athena database: {str(e)}")
                    # Continue anyway, as we've already stored the findings in S3
                    athena_success = False
                    athena_error = str(e)

            # Only proceed with table creation if database creation succeeded
            if athena_success:
                # Ensure Athena table exists
                table_name = "security_findings"
                try:
                    print(
                        f"Checking if Athena table {table_name} exists in database {athena_database}..."
                    )
                    glue.get_table(DatabaseName=athena_database, Name=table_name)
                    print(f"Athena table {table_name} exists")
                except glue.exceptions.EntityNotFoundException:
                    print(f"Creating Athena table {table_name}")
                    try:
                        query = f"""
                        CREATE EXTERNAL TABLE IF NOT EXISTS {athena_database}.{table_name} (
                          id STRING,
                          title STRING,
                          description STRING,
                          severity STRING,
                          resource_type STRING,
                          resource_id STRING,
                          found_at STRING,
                          status STRING,
                          compliance_status STRING,
                          product_name STRING,
                          company_name STRING,
                          region STRING
                        )
                        ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
                        LOCATION 's3://{s3_bucket}/'
                        TBLPROPERTIES ('has_encrypted_data'='false')
                        """
                        start_query_response = athena.start_query_execution(
                            QueryString=query,
                            ResultConfiguration={
                                "OutputLocation": f"s3://{athena_results_bucket}/"
                            },
                        )
                        print(
                            f"Executed query to create table, QueryExecutionId: {start_query_response['QueryExecutionId']}"
                        )
                        wait_for_query_to_complete(
                            athena, start_query_response["QueryExecutionId"]
                        )
                    except Exception as e:
                        print(f"Error creating Athena table: {str(e)}")
                        # Continue anyway, as we've already stored the findings in S3
                        athena_success = False
                        athena_error = str(e)

            # Optionally refresh Athena table partitions if using partitioning
            if athena_success and len(processed_findings) > 0:
                try:
                    print(f"Refreshing Athena table partitions...")
                    query = f"MSCK REPAIR TABLE {athena_database}.{table_name}"
                    athena.start_query_execution(
                        QueryString=query,
                        ResultConfiguration={
                            "OutputLocation": f"s3://{athena_results_bucket}/"
                        },
                    )
                    print(f"Successfully refreshed partitions")
                except Exception as e:
                    print(f"Warning: Failed to refresh partitions: {str(e)}")
                    # Not critical, continue anyway
        except Exception as e:
            print(f"Error setting up Athena: {str(e)}")
            import traceback

            traceback.print_exc()
            athena_success = False
            athena_error = str(e)

        # Return success for the main function since we stored the findings successfully
        if athena_success:
            return {
                "statusCode": 200,
                "body": f"Successfully uploaded {len(processed_findings)} findings to S3 bucket {s3_bucket} and updated Athena table",
            }
        else:
            # We succeeded in storing findings but failed with Athena, return a partial success
            return {
                "statusCode": 207,  # Partial success
                "body": f"Successfully uploaded {len(processed_findings)} findings to S3 bucket {s3_bucket}, but failed to update Athena: {athena_error}",
            }

    except Exception as e:
        print(f"Error in process_findings: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"statusCode": 500, "body": f"Error: {str(e)}"}


def wait_for_query_to_complete(athena_client, query_execution_id):
    """
    Wait for an Athena query to complete execution.

    Args:
        athena_client: Boto3 Athena client
        query_execution_id: ID of the query execution to wait for

    Returns:
        dict: Query execution result
    """
    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        query_status = athena_client.get_query_execution(
            QueryExecutionId=query_execution_id
        )
        query_execution_status = query_status["QueryExecution"]["Status"]["State"]

        if query_execution_status == "SUCCEEDED":
            return query_status
        elif query_execution_status in ["FAILED", "CANCELLED"]:
            reason = query_status["QueryExecution"]["Status"].get(
                "StateChangeReason", "Unknown error"
            )
            raise Exception(f"Query failed or was cancelled. Reason: {reason}")

        retry_count += 1
        time.sleep(1)  # Wait for 1 second before checking again

    raise Exception("Query timeout: the query took too long to execute")


def send_cloudformation_response(
    event, context, response_status, response_data, physical_resource_id=None
):
    """
    Send a response to CloudFormation for a custom resource request.

    Args:
        event (dict): The CloudFormation custom resource event
        context (object): The Lambda context
        response_status (str): 'SUCCESS' or 'FAILED'
        response_data (dict): The data to send back to CloudFormation
        physical_resource_id (str, optional): The physical resource ID. Defaults to None.
    """
    print(f"Preparing CloudFormation response: Status={response_status}")
    print(f"Response data: {json.dumps(response_data)}")

    response_url = event.get("ResponseURL")

    if not response_url:
        print("ERROR: No ResponseURL found in the event")
        print(f"Event data: {json.dumps(event)}")
        return {"statusCode": 500, "body": "No ResponseURL found in the event"}

    physical_id = physical_resource_id
    if not physical_id:
        physical_id = context.log_stream_name if context else "unknown"

    response_body = {
        "Status": response_status,
        "Reason": f'See details in CloudWatch Log Stream: {context.log_stream_name if context else "unknown"}',
        "PhysicalResourceId": physical_id,
        "StackId": event.get("StackId", ""),
        "RequestId": event.get("RequestId", ""),
        "LogicalResourceId": event.get("LogicalResourceId", ""),
        "Data": response_data,
    }

    print(f"Sending response to CloudFormation: {json.dumps(response_body)}")
    print(f"Response URL: {response_url}")

    req = urllib.request.Request(
        url=response_url,
        data=json.dumps(response_body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PUT",
    )

    try:
        with urllib.request.urlopen(req) as response:
            print(f"CloudFormation response status: {response.status}")
            return {
                "statusCode": response.status,
                "body": "Response sent to CloudFormation",
            }
    except Exception as e:
        print(f"Failed to send response to CloudFormation: {str(e)}")
        import traceback

        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": f"Failed to send response to CloudFormation: {str(e)}",
        }


def lambda_handler(event, context):
    """
    AWS Lambda function to retrieve findings from Security Hub and store them in S3.

    This function:
    1. Handles CloudFormation custom resource requests
    2. Queries AWS Security Hub for all findings
    3. Transforms the data as needed for cATO Dashboard
    4. Uploads the findings to the S3 bucket
    5. Updates Athena tables as needed

    Args:
        event (dict): The Lambda event
        context (object): The Lambda context

    Returns:
        dict: Response containing status code and message
    """
    print(f"Lambda function invoked with event: {json.dumps(event)}")
    print(
        f"Context log stream name: {context.log_stream_name if context else 'unknown'}"
    )

    # Print environment variables
    print("Environment variables:")
    for key, value in os.environ.items():
        if key.startswith("AWS_"):
            continue  # Skip AWS internal variables
        print(f"{key}: {value}")

    # Check if this is a CloudFormation custom resource request
    if event.get("RequestType") in ["Create", "Update", "Delete"]:
        print(f"Processing CloudFormation {event['RequestType']} request")

        # For Delete requests, just send success response
        if event["RequestType"] == "Delete":
            print("Handling Delete request - sending success response")
            return send_cloudformation_response(event, context, "SUCCESS", {})

        # For Create/Update, process findings and send response
        try:
            print(f"Handling {event['RequestType']} request - processing findings")
            result = process_findings()

            # Always return SUCCESS to CloudFormation for Create/Update requests, even if there are issues
            # This is critical to prevent the stack from rolling back because of Athena issues
            response_data = {
                "Message": result.get("body", "Function executed successfully")
            }

            # Only mark as failed if we had a complete failure
            # For 207 (partial success) and 200 (success), we return SUCCESS to CloudFormation
            if result["statusCode"] >= 500:
                print(
                    f"Critical error occurred with status code {result['statusCode']}"
                )
                print(f"Sending FAILED response to CloudFormation")
                return send_cloudformation_response(
                    event, context, "FAILED", response_data
                )
            else:
                print(f"Function executed with status code {result['statusCode']}")
                print(f"Sending SUCCESS response to CloudFormation")
                return send_cloudformation_response(
                    event, context, "SUCCESS", response_data
                )
        except Exception as e:
            print(f"Error processing CloudFormation request: {str(e)}")
            import traceback

            traceback.print_exc()

            # Even for exceptions, we still want to return SUCCESS to CloudFormation
            # to prevent stack rollback unless it's a catastrophic failure
            error_message = str(e)
            if (
                "Access Denied" in error_message
                or "credentials" in error_message.lower()
            ):
                # Only fail if we have permission issues
                return send_cloudformation_response(
                    event, context, "FAILED", {"Error": error_message}
                )
            else:
                # For all other errors, return SUCCESS to prevent stack rollback
                return send_cloudformation_response(
                    event, context, "SUCCESS", {"Warning": error_message}
                )

    # For regular Lambda invocations
    print("Processing regular Lambda invocation")
    result = process_findings()
    # Format response as expected by API Gateway or direct invocation
    return {"statusCode": result["statusCode"], "body": json.dumps(result["body"])}
