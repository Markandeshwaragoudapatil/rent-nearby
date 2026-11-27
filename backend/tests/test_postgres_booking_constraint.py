import os
import uuid
import pytest
from sqlalchemy.exc import IntegrityError

from app import create_app
from app.extensions import db
from app.models import Booking, Category, Product, RentalPricing, User
from config import TestingConfig, normalize_database_url

@pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="PostgreSQL CI database is not configured")
def test_postgres_rejects_overlapping_reserved_bookings():
    class PostgresTestConfig(TestingConfig):
        SQLALCHEMY_DATABASE_URI = normalize_database_url(os.environ["DATABASE_URL"])

    app = create_app(PostgresTestConfig)
    with app.app_context():
        suffix = uuid.uuid4().hex
        owner = User(name="Owner", email=f"owner-{suffix}@example.test", password_hash="x", role="OWNER")
        renter_one = User(name="Renter One", email=f"renter-one-{suffix}@example.test", password_hash="x")
        renter_two = User(name="Renter Two", email=f"renter-two-{suffix}@example.test", password_hash="x")
        category = Category(name=f"Category {suffix}", slug=f"category-{suffix}")
        db.session.add_all([owner, renter_one, renter_two, category])
        db.session.flush()
        product = Product(
            owner_id=owner.id, category_id=category.id, title="Concurrency test product",
            description="Temporary database constraint test", condition="GOOD",
            locality="Bengaluru", city="Bengaluru", status="ACTIVE"
        )
        product.pricing = RentalPricing(daily_price_paise=10000, deposit_paise=0)
        db.session.add(product)
        db.session.flush()
        first = Booking(
            renter_id=renter_one.id, product_id=product.id,
            start_date=__import__("datetime").date(2030, 1, 10),
            end_date=__import__("datetime").date(2030, 1, 15),
            rental_paise=50000, deposit_paise=0, fee_paise=0,
            total_paise=50000, status="ACCEPTED"
        )
        db.session.add(first)
        db.session.flush()
        second = Booking(
            renter_id=renter_two.id, product_id=product.id,
            start_date=__import__("datetime").date(2030, 1, 12),
            end_date=__import__("datetime").date(2030, 1, 17),
            rental_paise=50000, deposit_paise=0, fee_paise=0,
            total_paise=50000, status="CONFIRMED"
        )
        db.session.add(second)
        with pytest.raises(IntegrityError):
            db.session.flush()
        db.session.rollback()
