import boto3
import os

def send_notification(message):
    sns = boto3.client('sns')
    
    sns.publish(
        TopicArn=os.environ['SNS_TOPIC_ARN'],
        Subject='AWS Daily Billing Alert',
        Message=message
    )