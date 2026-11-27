def test_categories_start_empty(client):
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert response.get_json()["items"] == []

def test_products_returns_pagination(client):
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert response.get_json() == {"items": [], "page": 1, "per_page": 20, "total": 0}

def test_invalid_pagination_is_rejected(client):
    assert client.get("/api/v1/products?page=abc").status_code == 400
