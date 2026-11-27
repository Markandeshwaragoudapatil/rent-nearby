from datetime import date, timedelta

from app.extensions import db
from app.models import AvailabilityBlock, Category, Product, RentalPricing, User

def test_owner_blocked_dates_make_product_unavailable(app, client):
    with app.app_context():
        owner = User(name="Owner", email="availability-owner@example.com", password_hash="x", role="OWNER")
        category = Category(name="Availability Test", slug="availability-test")
        db.session.add_all([owner, category])
        db.session.flush()
        product = Product(owner_id=owner.id, category_id=category.id, title="Tripod",
                          description="Test tripod", condition="GOOD", locality="Bengaluru",
                          city="Bengaluru", status="ACTIVE")
        product.pricing = RentalPricing(daily_price_paise=10000)
        db.session.add(product)
        db.session.commit()
        owner_id, product_id = str(owner.id), str(product.id)
    with client.session_transaction() as session:
        session["user_id"] = owner_id
    start = date.today() + timedelta(days=4)
    end = start + timedelta(days=2)
    created = client.post(f"/api/v1/owner/products/{product_id}/availability-blocks", json={
        "start_date": start.isoformat(), "end_date": end.isoformat(), "reason": "Owner using it"
    })
    assert created.status_code == 201
    checked = client.get(f"/api/v1/products/{product_id}/availability", query_string={
        "start_date": start.isoformat(), "end_date": end.isoformat()
    })
    assert checked.status_code == 200
    assert checked.get_json()["available"] is False
