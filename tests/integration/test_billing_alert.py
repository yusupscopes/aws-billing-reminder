import pytest
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from aws_billing_reminder.lambdas.billing_alert.main import handler
from aws_billing_reminder.lambdas.billing_alert.cost_explorer import get_cost_data
from aws_billing_reminder.lambdas.billing_alert.notification import send_notification

def get_mock_ce_response():
    return {
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

def test_complete_workflow(ce_client, sns_client):
    """
    Integration test that verifies the complete workflow:
    1. Get cost data from Cost Explorer
    2. Format the message
    3. Send notification via SNS
    """
    with patch('boto3.client') as mock_boto3:
        # Configure the CE client mock
        mock_ce = MagicMock()
        mock_ce.get_cost_and_usage.return_value = get_mock_ce_response()
        
        # Configure boto3.client to return our mock CE or the moto sns_client
        def mock_client(service, *args, **kwargs):
            if service == 'ce':
                return mock_ce
            elif service == 'sns':
                return sns_client
        mock_boto3.side_effect = mock_client

        # Step 1: Get cost data directly
        today = datetime.now()
        first_day = today.replace(day=1).strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        
        cost_data = get_cost_data(first_day, today_str)
        assert isinstance(cost_data, dict)
        assert 'total' in cost_data
        assert 'by_service' in cost_data
        assert cost_data['total'] == 150.75  # 100.50 + 50.25
        
        # Step 2: Trigger the Lambda handler
        response = handler({}, {})
        assert response['statusCode'] == 200
        assert json.loads(response['body']) == 'Cost alert sent successfully'

        # Verify CE was called with correct parameters
        mock_ce.get_cost_and_usage.assert_called_with(
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

def test_error_scenarios(ce_client, sns_client):
    """Test various error scenarios in the workflow"""
    
    with patch('boto3.client') as mock_boto3:
        # Configure the CE client mock to raise an exception
        mock_ce = MagicMock()
        mock_ce.get_cost_and_usage.side_effect = Exception("Invalid date format")
        
        # Configure boto3.client to return our mock CE or the moto sns_client
        def mock_client(service, *args, **kwargs):
            if service == 'ce':
                return mock_ce
            elif service == 'sns':
                return sns_client
        mock_boto3.side_effect = mock_client

        # Test with invalid dates
        response = handler({}, {})
        assert response['statusCode'] == 500
        assert 'Error occurred' in response['body']
        
        # Test with missing SNS topic
        del os.environ['SNS_TOPIC_ARN']
        response = handler({}, {})
        assert response['statusCode'] == 500
        assert 'Error occurred' in response['body']

def test_cost_data_accuracy(ce_client):
    """Test accuracy of cost calculations"""
    
    with patch('boto3.client') as mock_boto3:
        # Configure the CE client mock
        mock_ce = MagicMock()
        mock_ce.get_cost_and_usage.return_value = get_mock_ce_response()
        mock_boto3.return_value = mock_ce

        # Get costs for last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        cost_data = get_cost_data(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        # Verify total matches sum of services
        services_total = sum(cost_data['by_service'].values())
        assert abs(cost_data['total'] - services_total) < 0.01  # Account for floating point
        assert cost_data['total'] == 150.75
        assert cost_data['by_service'] == {
            'AmazonEC2': 100.50,
            'AmazonS3': 50.25
        }