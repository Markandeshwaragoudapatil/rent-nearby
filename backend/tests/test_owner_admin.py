import uuid

from sqlalchemy import select

from app.extensions import db
from app.models import AuditLog, Category, Product, RentalPricing, User


def register(client, email="person@example.com"):
    response = client.post("/api/v1/auth/register", json={
        "name": "Test Person",
        "email": email,
        "password": "correct horse battery staple",
    })
    assert response.status_code == 201
    return response.get_json()["user"]


def promote_to_admin(app, user_id):
    with app.app_context():
        user = db.session.get(User, uuid.UUID(user_id))
        user.role = "ADMIN"
        user.verification_status = "VERIFIED"
        db.session.commit()


def apply_for_owner(client):
    return client.post("/api/v1/owner/application", json={
        "business_name": "Patil Equipment Rentals",
        "description": "I plan to rent cameras, power tools and event equipment in Bengaluru.",
        "contact_phone": "+91 9876543210",
        "city": "Bengaluru",
    })


def login_as(client, email):
    client.post("/api/v1/auth/logout")
    return client.post("/api/v1/auth/login", json={"email": email, "password": "correct horse battery staple"})


def test_renter_can_apply_but_is_not_promoted_automatically(client):
    register(client)
    response = apply_for_owner(client)
    assert response.status_code == 201
    assert response.get_json()["application"]["status"] == "PENDING"
    assert client.get("/api/v1/owner/products").status_code == 403
    assert client.get("/api/v1/owner/application").get_json()["application"]["status"] == "PENDING"


def test_owner_application_requires_authentication(client):
    assert client.post("/api/v1/owner/application", json={}).status_code == 401


def test_owner_application_validates_contact_and_description(client):
    register(client)
    response = client.post("/api/v1/owner/application", json={
        "business_name": "Rental business", "description": "Too short",
        "contact_phone": "123", "city": "Bengaluru",
    })
    assert response.status_code == 422


def test_non_admin_cannot_review_owner_application(client):
    register(client)
    application = apply_for_owner(client).get_json()["application"]
    response = client.patch(f"/api/v1/admin/owner-applications/{application['id']}/decision", json={"decision": "APPROVE"})
    assert response.status_code == 403


def test_admin_approval_grants_owner_and_writes_audit_log(app, client):
    register(client)
    application = apply_for_owner(client).get_json()["application"]
    admin = register(client, "admin@example.com")
    promote_to_admin(app, admin["id"])
    login_as(client, "admin@example.com")
    response = client.patch(f"/api/v1/admin/owner-applications/{application['id']}/decision", json={"decision": "APPROVE", "note": "Business details reviewed."})
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "OWNER"
    assert response.get_json()["user"]["verification_status"] == "VERIFIED"
    with app.app_context():
        assert db.session.scalar(select(AuditLog).where(AuditLog.resource_type == "owner_application"))


def test_rejection_requires_a_reason_and_allows_resubmission(app, client):
    register(client)
    application = apply_for_owner(client).get_json()["application"]
    admin = register(client, "admin@example.com")
    promote_to_admin(app, admin["id"])
    login_as(client, "admin@example.com")
    url = f"/api/v1/admin/owner-applications/{application['id']}/decision"
    assert client.patch(url, json={"decision": "REJECT"}).status_code == 422
    assert client.patch(url, json={"decision": "REJECT", "note": "Please provide clearer business details."}).status_code == 200
    login_as(client, "person@example.com")
    assert apply_for_owner(client).status_code == 201


def test_admin_can_approve_listing_and_public_catalogue_only_shows_active(app, client):
    renter = register(client)
    application = apply_for_owner(client).get_json()["application"]
    admin = register(client, "admin@example.com")
    promote_to_admin(app, admin["id"])
    login_as(client, "admin@example.com")
    client.patch(f"/api/v1/admin/owner-applications/{application['id']}/decision", json={"decision": "APPROVE"})
    login_as(client, "person@example.com")

    with app.app_context():
        category = Category(name="Electronics", slug="electronics")
        db.session.add(category)
        db.session.flush()
        product = Product(owner_id=uuid.UUID(renter["id"]), category_id=category.id, title="Camera", description="Mirrorless camera", condition="GOOD", locality="Kattigenahalli", status="PENDING_REVIEW")
        product.pricing = RentalPricing(daily_price_paise=100000)
        db.session.add(product)
        db.session.commit()
        product_id = str(product.id)

    login_as(client, "admin@example.com")
    pending = client.get("/api/v1/admin/products/pending")
    assert pending.status_code == 200
    assert pending.get_json()["items"][0]["id"] == product_id
    decision = client.patch(f"/api/v1/admin/products/{product_id}/decision", json={"decision": "APPROVE"})
    assert decision.status_code == 200
    assert decision.get_json()["product"]["status"] == "ACTIVE"
    assert client.get("/api/v1/products").get_json()["total"] == 1


def test_listing_rejection_keeps_it_out_of_public_catalogue(app, client):
    renter = register(client)
    admin = register(client, "admin@example.com")
    promote_to_admin(app, admin["id"])
    with app.app_context():
        category = Category(name="Tools", slug="tools")
        db.session.add(category)
        db.session.flush()
        product = Product(owner_id=uuid.UUID(renter["id"]), category_id=category.id, title="Drill", description="Cordless drill", condition="GOOD", locality="Yelahanka", status="PENDING_REVIEW")
        product.pricing = RentalPricing(daily_price_paise=50000)
        db.session.add(product)
        db.session.commit()
        product_id = str(product.id)
    login_as(client, "admin@example.com")
    response = client.patch(f"/api/v1/admin/products/{product_id}/decision", json={"decision": "REJECT", "note": "Please add clearer condition details."})
    assert response.status_code == 200
    assert client.get("/api/v1/products").get_json()["total"] == 0
