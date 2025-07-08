import logging
import json
from datetime import datetime, timedelta
from app.services.cost_explorer import get_cost_data, create_cost_message
from app.services.notification import send_notification

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    try:
        # Get today's date and first day of the month
        today = datetime.now()
        first_day = today.replace(day=1).strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        
        # Get cost data
        logger.info(f"Getting cost data for {first_day} to {today_str}")
        cost_data = get_cost_data(first_day, today_str)
        logger.info(f"Cost data: {cost_data}")
        
        # Prepare message
        message = create_cost_message(cost_data)
        logger.info(f"Message: {message}")
        
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

