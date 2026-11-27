def test_register_creates_renter(client):
    response = client.post("/api/v1/auth/register", json={"name": "Test Renter", "email": "renter@example.com", "password": "correct horse battery staple"})
    assert response.status_code == 201
    assert response.get_json()["user"]["role"] == "RENTER"
    assert "password_hash" not in response.get_json()["user"]

def test_register_ignores_user_supplied_admin_role(client):
    response = client.post("/api/v1/auth/register", json={"name": "Test User", "email": "test@example.com", "password": "correct horse battery staple", "role": "ADMIN"})
    assert response.status_code == 201
    assert response.get_json()["user"]["role"] == "RENTER"

def test_me_requires_authentication(client):
    assert client.get("/api/v1/auth/me").status_code == 401

def test_login_logout_flow(client):
    client.post("/api/v1/auth/register", json={"name": "Test", "email": "test@example.com", "password": "correct horse battery staple"})
    assert client.get("/api/v1/auth/me").status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401
