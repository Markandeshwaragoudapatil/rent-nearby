import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class Category(db.Model):
    __tablename__ = "categories"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(90), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class Product(db.Model):
    __tablename__ = "products"
    __table_args__ = (Index("ix_products_public_search", "status", "category_id", "created_at"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(140), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    condition: Mapped[str] = mapped_column(String(20), nullable=False)
    locality: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(100), default="Bengaluru", nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="DRAFT", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    category: Mapped[Category] = relationship()
    images: Mapped[list["ProductImage"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    pricing: Mapped["RentalPricing"] = relationship(back_populates="product", uselist=False, cascade="all, delete-orphan")
    def to_dict(self):
        return {"id": str(self.id), "title": self.title, "description": self.description, "condition": self.condition,
                "locality": self.locality, "city": self.city, "status": self.status,
                "category": {"id": str(self.category.id), "name": self.category.name, "slug": self.category.slug},
                "images": [{"url": image.image_url, "is_primary": image.is_primary} for image in self.images],
                "pricing": self.pricing.to_dict() if self.pricing else None}

class ProductImage(db.Model):
    __tablename__ = "product_images"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    asset_id: Mapped[str | None] = mapped_column(String(255))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    product: Mapped[Product] = relationship(back_populates="images")

class RentalPricing(db.Model):
    __tablename__ = "rental_pricing"
    __table_args__ = (
        CheckConstraint("hourly_price_paise >= 0 AND daily_price_paise >= 0 AND deposit_paise >= 0", name="ck_rental_prices_nonnegative"),
        CheckConstraint("hourly_price_paise > 0 OR daily_price_paise > 0", name="ck_rental_at_least_one_price"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False)
    hourly_price_paise: Mapped[int] = mapped_column(default=0, nullable=False)
    daily_price_paise: Mapped[int] = mapped_column(default=0, nullable=False)
    deposit_paise: Mapped[int] = mapped_column(default=0, nullable=False)
    product: Mapped[Product] = relationship(back_populates="pricing")
    def to_dict(self):
        return {"hourly_price_paise": self.hourly_price_paise, "daily_price_paise": self.daily_price_paise, "deposit_paise": self.deposit_paise}
