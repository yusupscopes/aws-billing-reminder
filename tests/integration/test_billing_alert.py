import pytest
import os
import sys
import json
from datetime import datetime

from src.aws_billing_reminder.lambdas.billing_alert.main import handler
from src.aws_billing_reminder.lambdas.billing_alert.cost_explorer import get_cost_data
from src.aws_billing_reminder.lambdas.billing_alert.notification import send_notification

def test_complete_workflow(ce_client, sns_client):
    """
    Integration test that verifies the complete workflow:
    1. Get cost data from Cost Explorer
    2. Format the message
    3. Send notification via SNS
    """
    # Step 1: Get cost data directly
    today = datetime.now()
    first_day = today.replace(day=1).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    
    cost_data = get_cost_data(first_day, today_str)
    assert isinstance(cost_data, dict)
    assert 'total' in cost_data
    assert 'by_service' in cost_data
    
    # Step 2: Trigger the Lambda handler
    response = handler({}, {})
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == 'Cost alert sent successfully'
    
    # Note: With moto, we can't verify the actual SNS message delivery,
    # but we can verify that all steps completed successfully
