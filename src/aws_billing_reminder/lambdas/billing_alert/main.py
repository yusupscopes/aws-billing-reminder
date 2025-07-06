import json
from datetime import datetime, timedelta
from aws_billing_reminder.lambdas.billing_alert.cost_explorer import get_cost_data, create_cost_message
from aws_billing_reminder.lambdas.billing_alert.notification import send_notification

def handler(event, context):
    try:
        # Get today's date and first day of the month
        today = datetime.now()
        first_day = today.replace(day=1).strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        
        # Get cost data
        cost_data = get_cost_data(first_day, today_str)
        
        # Prepare message
        message = create_cost_message(cost_data)
        
        # Send notification
        send_notification(message)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Cost alert sent successfully')
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error occurred: {str(e)}')
        }

