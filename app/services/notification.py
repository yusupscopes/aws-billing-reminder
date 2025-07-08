import boto3
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def send_notification(message):
    logger.info(f"Message length: {len(message.encode('utf-8'))} bytes")
    logger.info(f"SNS Topic ARN: {os.environ.get('SNS_TOPIC_ARN')}")
    # Check message size (256 KiB = 256 * 1024 bytes)
    if len(message.encode('utf-8')) >= 256 * 1024:
        raise ValueError("Message size exceeds SNS limit of 256 KiB")
    
    if not os.environ['SNS_TOPIC_ARN']:
        raise ValueError("SNS_TOPIC_ARN is not set")
    
    sns = boto3.client('sns')

    try:
        response = sns.publish(
            TopicArn=os.environ.get('SNS_TOPIC_ARN'),
            Subject='AWS Daily Billing Alert',
            Message=message
        )
        logger.info(f"SNS publish response: {response}")
        return response
    except Exception as e:
        logger.error(f"Failed to publish to SNS: {str(e)}")
        raise e