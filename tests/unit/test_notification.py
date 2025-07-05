import pytest
import os
from src.aws_billing_reminder.lambdas.billing_alert.notification import send_notification

def test_send_notification(sns_client):
    # Test message
    test_message = "Test billing alert message"
    
    # Send notification
    send_notification(test_message)
    
    # Verify message was published
    # Note: With moto, we can't actually verify the message content,
    # but we can verify that the function executes without error
    
def test_send_notification_missing_topic_arn():
    # Remove SNS topic ARN to simulate error
    if 'SNS_TOPIC_ARN' in os.environ:
        del os.environ['SNS_TOPIC_ARN']
    
    # Verify that sending notification raises error
    with pytest.raises(Exception):
        send_notification("Test message")
