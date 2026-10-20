import json


def test_api_transaction_requires_fields(client):
    """Missing fields should return 400."""
    response = client.post('/api/v1/transactions', 
                          data=json.dumps({'amount': 100}),
                          content_type='application/json')
    assert response.status_code == 400
    assert b'Missing transaction attributes' in response.data


def test_api_transaction_valid(client):
    """Valid transaction should be processed and saved."""
    payload = {
        'account_number': 'ACC-API-TEST',
        'amount': 5000,
        'location': 'Durban',
        'type': 'TRANSFER',
        'oldbalanceOrg': 10000,
        'newbalanceOrig': 5000,
        'oldbalanceDest': 0,
        'newbalanceDest': 5000
    }
    
    response = client.post('/api/v1/transactions',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert 'transaction_id' in json_data
    assert 'risk_score' in json_data
    assert json_data['decision'] in ['Flagged', 'Safe']


def test_api_transaction_invalid_amount(client):
    """Non-numeric amount should return 400."""
    payload = {
        'account_number': 'ACC-TEST',
        'amount': 'not-a-number',
        'location': 'JHB',
        'type': 'PAYMENT',
        'oldbalanceOrg': 0,
        'newbalanceOrig': 0
    }
    
    response = client.post('/api/v1/transactions',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 400
    assert b'Invalid amount format' in response.data