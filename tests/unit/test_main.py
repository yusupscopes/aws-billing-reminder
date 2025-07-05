import os
from src.aws_billing_reminder.lambdas.billing_alert.main import handler, create_cost_message

def test_handler_success(ce_client, sns_client):
    # Call handler
    response = handler({}, {})
    
    # Verify successful response
    assert response['statusCode'] == 200
    assert 'Cost alert sent successfully' in response['body']

def test_handler_error(ce_client):
    # Remove SNS topic ARN to cause error
    if 'SNS_TOPIC_ARN' in os.environ:
        del os.environ['SNS_TOPIC_ARN']
    
    # Call handler
    response = handler({}, {})
    
    # Verify error response
    assert response['statusCode'] == 500
    assert 'Error occurred' in response['body']

def test_create_cost_message():
    # Test data
    cost_data = {
        'total': 123.45,
        'by_service': {
            'AmazonEC2': 100.00,
            'AmazonS3': 23.45
        }
    }
    
    # Create message
    message = create_cost_message(cost_data)
    
    # Verify message content
    assert 'Total Month-to-Date Cost: $123.45' in message
    assert 'AmazonEC2: $100.00' in message
    assert 'AmazonS3: $23.45' in message
