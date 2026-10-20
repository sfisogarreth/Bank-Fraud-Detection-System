def test_dashboard_requires_login(client):
    """Dashboard should redirect to login when not authenticated."""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200
    # Should end up at login page
    assert b'Authorized Fraud Operators Only' in response.data


def test_dashboard_loads_when_logged_in(client):
    """Authenticated user should see dashboard."""
    # Login first
    client.post('/login', data={
        'email': 'test@mazi.ai',
        'password': 'TestPass123!'
    })
    
    response = client.get('/dashboard/')
    assert response.status_code == 200
    assert b'MAZI Threat Command Center' in response.data


def test_api_stats_json(client):
    """Dashboard stats API should return JSON."""
    response = client.get('/dashboard/api/stats')
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'transaction_count' in json_data
    assert 'active_alerts' in json_data


def test_health_endpoint(client):
    """Health check should return healthy status."""
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'healthy'
    assert json_data['database'] == 'sqlite'