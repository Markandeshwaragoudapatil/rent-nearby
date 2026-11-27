"""Create the initial RentNearby schema and reservation exclusion constraint.

Revision ID: 20261127_0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "20261127_0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(20), unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="RENTER"),
        sa.Column("verification_status", sa.String(20), nullable=False, server_default="UNVERIFIED"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("slug", sa.String(90), nullable=False, unique=True),
        sa.Column("description", sa.String(300)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "user_addresses",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(40), nullable=False, server_default="Home"),
        sa.Column("address", sa.String(300), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("pincode", sa.String(10), nullable=False),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
    )
    op.create_index("ix_user_addresses_user_id", "user_addresses", ["user_id"])

    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("category_id", sa.Uuid(), sa.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(140), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("condition", sa.String(20), nullable=False),
        sa.Column("locality", sa.String(120), nullable=False),
        sa.Column("city", sa.String(100), nullable=False, server_default="Bengaluru"),
        sa.Column("status", sa.String(24), nullable=False, server_default="DRAFT"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_products_owner_id", "products", ["owner_id"])
    op.create_index("ix_products_category_id", "products", ["category_id"])
    op.create_index("ix_products_public_search", "products", ["status", "category_id", "created_at"])

    op.create_table(
        "product_images",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("image_url", sa.String(1000), nullable=False),
        sa.Column("asset_id", sa.String(255)),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_product_images_product_id", "product_images", ["product_id"])

    op.create_table(
        "rental_pricing",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("hourly_price_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("daily_price_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deposit_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint("hourly_price_paise >= 0 AND daily_price_paise >= 0 AND deposit_paise >= 0", name="ck_rental_prices_nonnegative"),
        sa.CheckConstraint("hourly_price_paise > 0 OR daily_price_paise > 0", name="ck_rental_at_least_one_price"),
    )

    op.create_table(
        "bookings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("renter_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("rental_paise", sa.BigInteger(), nullable=False),
        sa.Column("deposit_paise", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("fee_paise", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_paise", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="PENDING"),
        sa.Column("idempotency_key", sa.String(100), unique=True),
        sa.Column("payment_deadline_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("start_date < end_date", name="ck_booking_valid_dates"),
        sa.CheckConstraint("rental_paise >= 0 AND deposit_paise >= 0 AND fee_paise >= 0 AND total_paise >= 0", name="ck_booking_amounts_nonnegative"),
        sa.CheckConstraint("status IN ('PENDING','ACCEPTED','REJECTED','PAYMENT_PENDING','CONFIRMED','ACTIVE','COMPLETED','CANCELLED','DISPUTED')", name="ck_booking_status"),
    )
    op.create_index("ix_bookings_renter_id", "bookings", ["renter_id"])
    op.create_index("ix_bookings_product_id", "bookings", ["product_id"])
    op.create_index("ix_bookings_product_dates", "bookings", ["product_id", "start_date", "end_date"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("booking_id", sa.Uuid(), sa.ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("amount_paise", sa.BigInteger(), nullable=False),
        sa.Column("provider_order_id", sa.String(100), unique=True),
        sa.Column("provider_payment_id", sa.String(100), unique=True),
        sa.Column("status", sa.String(24), nullable=False, server_default="CREATED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_payments_booking_id", "payments", ["booking_id"])

    op.create_table(
        "booking_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("booking_id", sa.Uuid(), sa.ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("actor_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("from_status", sa.String(24)),
        sa.Column("to_status", sa.String(24), nullable=False),
        sa.Column("note", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_booking_events_booking_id", "booking_events", ["booking_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("actor_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(80), nullable=False),
        sa.Column("resource_id", sa.Uuid()),
        sa.Column("details", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "payment_webhook_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("provider_event_id", sa.String(150), nullable=False, unique=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "availability_blocks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.String(200)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("start_date < end_date", name="ck_availability_block_dates"),
    )
    op.create_index("ix_availability_blocks_product_dates", "availability_blocks", ["product_id", "start_date", "end_date"])

    op.create_table(
        "reviews",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("booking_id", sa.Uuid(), sa.ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("reviewer_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
    )

    op.create_table(
        "disputes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("booking_id", sa.Uuid(), sa.ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("raised_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="OPEN"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_disputes_booking_id", "disputes", ["booking_id"])

    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute("""
        ALTER TABLE bookings
        ADD CONSTRAINT ex_bookings_no_overlapping_reservations
        EXCLUDE USING gist (
            product_id WITH =,
            daterange(start_date, end_date, '[)') WITH &&
        )
        WHERE (status IN ('ACCEPTED', 'PAYMENT_PENDING', 'CONFIRMED', 'ACTIVE'))
    """)

def downgrade():
    op.execute("ALTER TABLE bookings DROP CONSTRAINT IF EXISTS ex_bookings_no_overlapping_reservations")
    op.drop_index("ix_disputes_booking_id", table_name="disputes")
    op.drop_table("disputes")
    op.drop_table("reviews")
    op.drop_index("ix_availability_blocks_product_dates", table_name="availability_blocks")
    op.drop_table("availability_blocks")
    op.drop_table("payment_webhook_events")
    op.drop_table("audit_logs")
    op.drop_index("ix_booking_events_booking_id", table_name="booking_events")
    op.drop_table("booking_events")
    op.drop_index("ix_payments_booking_id", table_name="payments")
    op.drop_table("payments")
    op.drop_index("ix_bookings_product_dates", table_name="bookings")
    op.drop_index("ix_bookings_product_id", table_name="bookings")
    op.drop_index("ix_bookings_renter_id", table_name="bookings")
    op.drop_table("bookings")
    op.drop_table("rental_pricing")
    op.drop_index("ix_product_images_product_id", table_name="product_images")
    op.drop_table("product_images")
    op.drop_index("ix_products_public_search", table_name="products")
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_index("ix_products_owner_id", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_user_addresses_user_id", table_name="user_addresses")
    op.drop_table("user_addresses")
    op.drop_table("categories")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
