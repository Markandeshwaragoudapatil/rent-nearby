from datetime import date, timedelta

from app.extensions import db
from app.models import Category, Product, RentalPricing, User

def make_user(email, role):
    user = User(name=role.title(), email=email, password_hash="not-used-in-this-test", role=role)
    db.session.add(user)
    db.session.flush()
    return user

def make_product(owner):
    category = Category(name="Test Electronics", slug="test-electronics")
    db.session.add(category)
    db.session.flush()
    product = Product(
        owner_id=owner.id, category_id=category.id, title="Test camera",
        description="A test camera", condition="GOOD", locality="Kattigenahalli",
        city="Bengaluru", status="ACTIVE"
    )
    product.pricing = RentalPricing(daily_price_paise=50000, deposit_paise=100000)
    db.session.add(product)
    db.session.commit()
    return product

def sign_in(client, user_id):
    with client.session_transaction() as session:
        session["user_id"] = str(user_id)

def setup_marketplace(app):
    with app.app_context():
        owner = make_user("owner@example.com", "OWNER")
        renter = make_user("renter@example.com", "RENTER")
        product = make_product(owner)
        return str(owner.id), str(renter.id), str(product.id)

def test_booking_request_calculates_server_side_total(app, client):
    owner_id, renter_id, product_id = setup_marketplace(app)
    sign_in(client, renter_id)
    start = date.today() + timedelta(days=2)
    end = start + timedelta(days=3)
    response = client.post("/api/v1/bookings", json={
        "product_id": product_id, "start_date": start.isoformat(), "end_date": end.isoformat(),
        "rental_paise": 1, "deposit_paise": 1, "total_paise": 1
    })
    assert response.status_code == 201
    booking = response.get_json()["booking"]
    assert booking["rental_paise"] == 150000
    assert booking["deposit_paise"] == 100000
    assert booking["total_paise"] == 250000
    assert booking["status"] == "PENDING"

def test_only_one_overlapping_pending_request_can_be_accepted(app, client):
    owner_id, renter_id, product_id = setup_marketplace(app)
    with app.app_context():
        second_renter = make_user("second@example.com", "RENTER")
        second_renter_id = str(second_renter.id)
        db.session.commit()
    sign_in(client, renter_id)
    start = date.today() + timedelta(days=5)
    end = start + timedelta(days=2)
    first = client.post("/api/v1/bookings", json={
        "product_id": product_id, "start_date": start.isoformat(), "end_date": end.isoformat()
    }).get_json()["booking"]
    sign_in(client, second_renter_id)
    second = client.post("/api/v1/bookings", json={
        "product_id": product_id, "start_date": start.isoformat(), "end_date": end.isoformat()
    }).get_json()["booking"]
    sign_in(client, owner_id)
    accepted = client.post(f"/api/v1/owner/bookings/{first['id']}/accept")
    rejected_by_conflict = client.post(f"/api/v1/owner/bookings/{second['id']}/accept")
    assert accepted.status_code == 200
    assert accepted.get_json()["booking"]["status"] == "ACCEPTED"
    assert rejected_by_conflict.status_code == 409

def test_adjacent_date_ranges_do_not_overlap(app, client):
    owner_id, renter_id, product_id = setup_marketplace(app)
    sign_in(client, renter_id)
    start = date.today() + timedelta(days=10)
    middle = start + timedelta(days=2)
    end = middle + timedelta(days=2)
    first = client.post("/api/v1/bookings", json={
        "product_id": product_id, "start_date": start.isoformat(), "end_date": middle.isoformat()
    }).get_json()["booking"]
    sign_in(client, owner_id)
    assert client.post(f"/api/v1/owner/bookings/{first['id']}/accept").status_code == 200
    sign_in(client, renter_id)
    second_response = client.post("/api/v1/bookings", json={
        "product_id": product_id, "start_date": middle.isoformat(), "end_date": end.isoformat()
    })
    assert second_response.status_code == 201

def test_booking_idempotency_key_prevents_duplicate_requests(app, client):
    owner_id, renter_id, product_id = setup_marketplace(app)
    sign_in(client, renter_id)
    start = date.today() + timedelta(days=15)
    payload = {"product_id": product_id, "start_date": start.isoformat(), "end_date": (start + timedelta(days=1)).isoformat()}
    first = client.post("/api/v1/bookings", json=payload, headers={"Idempotency-Key": "rentnearby-test-key"})
    second = client.post("/api/v1/bookings", json=payload, headers={"Idempotency-Key": "rentnearby-test-key"})
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.get_json()["booking"]["id"] == second.get_json()["booking"]["id"]
