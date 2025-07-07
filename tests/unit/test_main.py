import os
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.main import handler, create_cost_message

def test_handler_success(ce_client, sns_client):
    # Mock response from Cost Explorer
    mock_ce_response = {
        'ResultsByTime': [{
            'Groups': [
                {
                    'Keys': ['AmazonEC2'],
                    'Metrics': {
                        'UnblendedCost': {
                            'Amount': '100.50',
                            'Unit': 'USD'
                        }
                    }
                },
                {
                    'Keys': ['AmazonS3'],
                    'Metrics': {
                        'UnblendedCost': {
                            'Amount': '50.25',
                            'Unit': 'USD'
                        }
                    }
                }
            ]
        }]
    }

    # Patch the get_cost_and_usage method
    with patch('boto3.client') as mock_boto3:
        # Configure the CE client mock
        mock_ce = MagicMock()
        mock_ce.get_cost_and_usage.return_value = mock_ce_response
        
        # Configure the SNS client mock to use the real moto sns_client
        def mock_client(service, *args, **kwargs):
            if service == 'ce':
                return mock_ce
            elif service == 'sns':
                return sns_client
        mock_boto3.side_effect = mock_client

        # Call handler
        response = handler({}, {})

        # Verify successful response
        assert response['statusCode'] == 200
        assert 'Cost alert sent successfully' in response['body']

        # Verify CE was called with correct parameters
        today = datetime.now()
        first_day = today.replace(day=1).strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        
        mock_ce.get_cost_and_usage.assert_called_once_with(
            TimePeriod={
                'Start': first_day,
                'End': today_str
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ]
        )

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
