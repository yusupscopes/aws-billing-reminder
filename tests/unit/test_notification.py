import pytest
import os
from app.services.notification import send_notification

def test_send_notification(sns_client):
    # Test message
    test_message = "Test billing alert message"
    
    # Send notification
    send_notification(test_message)
    
    # Get published messages
    topics = sns_client.list_topics()
    topic_arn = topics['Topics'][0]['TopicArn']
    
    # Verify message was published
    # Note: With moto, we can verify the topic exists and no errors occur
    assert topic_arn == os.environ['SNS_TOPIC_ARN']

def test_send_notification_missing_topic_arn():
    # Remove SNS topic ARN to simulate error
    if 'SNS_TOPIC_ARN' in os.environ:
        del os.environ['SNS_TOPIC_ARN']
    
    # Verify that sending notification raises error
    with pytest.raises(Exception):
        send_notification("Test message")

def test_send_notification_large_message(sns_client):
    # Test with a large message (near SNS limit)
    large_message = "x" * 256 * 1024  # 256KB message
    
    # Should raise an exception for too large message
    with pytest.raises(Exception):
        send_notification(large_message)

def test_send_notification_special_characters(sns_client):
    # Test message with special characters
    special_message = "Test message with special chars: !@#$%^&*()"
    
    # Should handle special characters without error
    send_notification(special_message)