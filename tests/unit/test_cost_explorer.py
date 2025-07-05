from src.aws_billing_reminder.lambdas.billing_alert.cost_explorer import get_cost_data

def test_get_cost_data(ce_client):
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

def test_get_cost_data_empty_response(ce_client):
    # Test with dates that should return no data
    start_date = "2023-01-01"
    end_date = "2023-01-02"
    
    # Get cost data
    result = get_cost_data(start_date, end_date)
    
    # Verify empty response handling
    assert result['total'] == 0
    assert result['by_service'] == {}
