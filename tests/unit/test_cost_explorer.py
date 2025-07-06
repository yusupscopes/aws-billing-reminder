import pytest
from datetime import datetime
from aws_billing_reminder.lambdas.billing_alert.cost_explorer import get_cost_data, create_cost_message
from unittest.mock import patch, MagicMock

def test_get_cost_data(ce_client):
    # Mock CE response
    mock_response = {
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

    # Mock the CE client
    with patch('boto3.client') as mock_boto3:
        mock_ce = MagicMock()
        mock_ce.get_cost_and_usage.return_value = mock_response
        mock_boto3.return_value = mock_ce

        # Test dates
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        # Get cost data
        result = get_cost_data(start_date, end_date)
        
        # Verify structure
        assert isinstance(result, dict)
        assert 'total' in result
        assert 'by_service' in result
        assert isinstance(result['total'], float)
        assert isinstance(result['by_service'], dict)
        
        # Verify values
        assert result['total'] == 150.75  # 100.50 + 50.25
        assert result['by_service'] == {
            'AmazonEC2': 100.50,
            'AmazonS3': 50.25
        }

        # Verify CE was called with correct parameters
        mock_ce.get_cost_and_usage.assert_called_once_with(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ]
        )

def test_get_cost_data_empty_response(ce_client):
    # Mock empty CE response
    mock_response = {
        'ResultsByTime': [{
            'Groups': []
        }]
    }

    with patch('boto3.client') as mock_boto3:
        mock_ce = MagicMock()
        mock_ce.get_cost_and_usage.return_value = mock_response
        mock_boto3.return_value = mock_ce

        # Test dates
        start_date = "2023-01-01"
        end_date = "2023-01-02"
        
        # Get cost data
        result = get_cost_data(start_date, end_date)
        
        # Verify empty response handling
        assert result['total'] == 0
        assert result['by_service'] == {}

def test_cost_data_formatting():
    # Test data
    test_data = {
        'total': 150.75,
        'by_service': {
            'AmazonEC2': 100.50,
            'AmazonS3': 50.25
        }
    }
    
    # Format message
    message = create_cost_message(test_data)
    
    # Verify message format
    assert isinstance(message, str)
    assert f"Total Month-to-Date Cost: $150.75" in message
    assert "AmazonEC2: $100.50" in message
    assert "AmazonS3: $50.25" in message
    assert datetime.now().strftime('%Y-%m-%d') in message

def test_error_handling(ce_client):
    # Test with invalid dates
    with patch('boto3.client') as mock_boto3:
        mock_ce = MagicMock()
        mock_ce.get_cost_and_usage.side_effect = Exception("Invalid date format")
        mock_boto3.return_value = mock_ce

        # Test with invalid dates
        with pytest.raises(Exception):
            get_cost_data("invalid-date", "2024-01-31")