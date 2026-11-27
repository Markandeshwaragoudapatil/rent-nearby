from flask import Blueprint, abort, g, jsonify, request
from sqlalchemy import select

from ..extensions import db
from ..models import Category, OwnerApplication, Product, RentalPricing
from ..security import login_required, roles_required

owner_bp = Blueprint("owner", __name__)


def payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, description="A JSON object is required.")
    return data


@owner_bp.post("/application")
@login_required
def submit_owner_application():
    if g.current_user.role == "ADMIN":
        abort(409, description="Administrator accounts cannot apply for owner access.")
    if g.current_user.role == "OWNER":
        abort(409, description="This account already has owner access.")
    data = payload()
    business_name = str(data.get("business_name", "")).strip()
    description = str(data.get("description", "")).strip()
    contact_phone = str(data.get("contact_phone", "")).strip()
    city = str(data.get("city", "Bengaluru")).strip()
    errors = {}
    if not business_name or len(business_name) > 120:
        errors["business_name"] = "Enter a name up to 120 characters."
    if len(description) < 30 or len(description) > 1500:
        errors["description"] = "Describe what you plan to rent out (30–1500 characters)."
    digits = "".join(character for character in contact_phone if character.isdigit())
    if not 10 <= len(digits) <= 15:
        errors["contact_phone"] = "Enter a valid contact number."
    if not city or len(city) > 100:
        errors["city"] = "Enter a valid city."
    if errors:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "Check the application details.", "fields": errors}}), 422

    application = db.session.scalar(select(OwnerApplication).where(OwnerApplication.user_id == g.current_user.id))
    if application and application.status in {"PENDING", "APPROVED"}:
        abort(409, description="An active or approved owner application already exists.")
    if application:
        application.business_name = business_name
        application.description = description
        application.contact_phone = contact_phone
        application.city = city
        application.status = "PENDING"
        application.decision_note = None
        application.reviewed_by = None
        application.reviewed_at = None
    else:
        application = OwnerApplication(user_id=g.current_user.id, business_name=business_name, description=description, contact_phone=contact_phone, city=city)
        db.session.add(application)
    db.session.commit()
    return jsonify({"application": application.to_dict()}), 201


@owner_bp.get("/application")
@login_required
def get_owner_application():
    application = db.session.scalar(select(OwnerApplication).where(OwnerApplication.user_id == g.current_user.id))
    return jsonify({"application": application.to_dict() if application else None})


@owner_bp.get("/products")
@roles_required("OWNER")
def list_products():
    rows = db.session.scalars(select(Product).where(Product.owner_id == g.current_user.id).order_by(Product.created_at.desc())).all()
    return jsonify({"items": [{"id": str(p.id), "title": p.title, "status": p.status, "locality": p.locality} for p in rows]})


@owner_bp.post("/products")
@roles_required("OWNER")
def create_product():
    data = payload()
    required = ("title", "description", "condition", "locality", "category_id")
    missing = [field for field in required if not str(data.get(field, "")).strip()]
    if missing:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "Required fields are missing.", "fields": {key: "Required." for key in missing}}}), 422
    if len(data["title"]) > 140 or len(data["description"]) > 5000:
        abort(422, description="Title or description is too long.")
    if data["condition"] not in {"NEW", "LIKE_NEW", "GOOD", "FAIR"}:
        abort(422, description="Unsupported condition.")
    category = db.session.get(Category, data["category_id"])
    if category is None or not category.is_active:
        abort(422, description="Select an active category.")
    try:
        hourly = int(data.get("hourly_price_paise", 0))
        daily = int(data.get("daily_price_paise", 0))
        deposit = int(data.get("deposit_paise", 0))
    except (ValueError, TypeError):
        abort(422, description="Prices must be integer paise.")
    if min(hourly, daily, deposit) < 0 or max(hourly, daily) <= 0 or max(hourly, daily, deposit) > 100000000:
        abort(422, description="Provide a valid positive rental price and non-negative deposit.")
    locality = str(data["locality"]).strip()
    if len(locality) > 120:
        abort(422, description="Locality is too long.")
    product = Product(owner_id=g.current_user.id, category_id=category.id, title=data["title"].strip(), description=data["description"].strip(), condition=data["condition"], locality=locality, status="DRAFT")
    product.pricing = RentalPricing(hourly_price_paise=hourly, daily_price_paise=daily, deposit_paise=deposit)
    db.session.add(product)
    db.session.commit()
    return jsonify({"product": {"id": str(product.id), "status": product.status}}), 201


@owner_bp.post("/products/<uuid:product_id>/submit")
@roles_required("OWNER")
def submit_product(product_id):
    product = db.session.scalar(select(Product).where(Product.id == product_id, Product.owner_id == g.current_user.id))
    if product is None:
        abort(404)
    if product.status not in {"DRAFT", "REJECTED"} or product.pricing is None:
        abort(409, description="Only complete draft listings can be submitted.")
    product.status = "PENDING_REVIEW"
    db.session.commit()
    return jsonify({"product": {"id": str(product.id), "status": product.status}})
