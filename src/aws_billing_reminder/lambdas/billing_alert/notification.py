import boto3
import os

def send_notification(message):
    # Check message size (256 KiB = 256 * 1024 bytes)
    if len(message.encode('utf-8')) >= 256 * 1024:
        raise ValueError("Message size exceeds SNS limit of 256 KiB")
    
    if not os.environ['SNS_TOPIC_ARN']:
        raise ValueError("SNS_TOPIC_ARN is not set")
    
    sns = boto3.client('sns')
    
    sns.publish(
        TopicArn=os.environ['SNS_TOPIC_ARN'],
        Subject='AWS Daily Billing Alert',
        Message=message
    )