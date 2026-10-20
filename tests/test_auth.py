def test_signup_page_loads(client):
    """GET /signup should return the signup form."""
    response = client.get('/signup')
    assert response.status_code == 200
    assert b'Operator Clearance Request' in response.data


def test_signup_with_weak_password(client):
    """Weak passwords should be rejected."""
    response = client.post('/signup', data={
        'username': 'newuser',
        'email': 'new@mazi.ai',
        'password': '123'  # Too weak
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'at least 8 characters' in response.data or b'Password must' in response.data


def test_signup_success(client):
    """Valid signup should create user and redirect to login."""
    response = client.post('/signup', data={
        'username': 'validuser',
        'email': 'valid@mazi.ai',
        'password': 'StrongPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Account created' in response.data or b'Please log in' in response.data


def test_login_page_loads(client):
    """GET /login should return the login form."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Authorized Fraud Operators Only' in response.data


def test_login_success(client):
    """Valid credentials should log in and redirect to dashboard."""
    response = client.post('/login', data={
        'email': 'test@mazi.ai',
        'password': 'TestPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'System Radar' in response.data or b'dashboard' in response.data.lower()


def test_login_invalid_password(client):
    """Wrong password should show error."""
    response = client.post('/login', data={
        'email': 'test@mazi.ai',
        'password': 'WrongPassword123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_logout(client):
    """Logout should clear session."""
    # First login
    client.post('/login', data={
        'email': 'test@mazi.ai',
        'password': 'TestPass123!'
    })
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out' in response.data or b'Sign Out' in response.data


def test_rate_limiting(client):
    """5 failed attempts should trigger rate limit."""
    for i in range(6):
        response = client.post('/login', data={
            'email': 'test@mazi.ai',
            'password': 'WrongPassword123!'
        }, follow_redirects=True)
    
    # 6th attempt should be rate limited
    assert b'Too many login attempts' in response.data or response.status_code == 429