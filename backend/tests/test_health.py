def test_health_checks_database(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok"}

def test_root_identifies_api(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["name"] == "RentNearby API"
