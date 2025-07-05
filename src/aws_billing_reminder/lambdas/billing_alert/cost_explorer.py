import boto3
from datetime import datetime

def get_cost_data(start_date, end_date):
    client = boto3.client('ce')
    
    response = client.get_cost_and_usage(
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
    
    total_cost = 0
    services_cost = {}
    
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            service = group['Keys'][0]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            services_cost[service] = cost
            total_cost += cost
    
    return {
        'total': total_cost,
        'by_service': services_cost
    }

def create_cost_message(cost_data):
    total_cost = cost_data['total']
    services = cost_data['by_service']
    
    message = f"AWS Billing Report - {datetime.now().strftime('%Y-%m-%d')}\n\n"
    message += f"Total Month-to-Date Cost: ${total_cost:.2f}\n\n"
    message += "Cost Breakdown by Service:\n"
    
    for service, cost in services.items():
        message += f"- {service}: ${cost:.2f}\n"
    
    return message