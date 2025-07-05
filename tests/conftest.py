import pytest
import boto3
from moto import mock_ce, mock_sns

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    import os
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture
def ce_client(aws_credentials):
    with mock_ce():
        yield boto3.client("ce", region_name="us-east-1")

@pytest.fixture
def sns_client(aws_credentials):
    with mock_sns():
        client = boto3.client("sns", region_name="us-east-1")
        # Create a test topic
        response = client.create_topic(Name="test-topic")
        topic_arn = response["TopicArn"]
        # Set environment variable for notification module
        import os
        os.environ["SNS_TOPIC_ARN"] = topic_arn
        yield client
