import json
from datetime import datetime, timezone

from flask import Blueprint, abort, g, jsonify, request
from sqlalchemy import select

from ..extensions import db
from ..models import AuditLog, OwnerApplication, Product, User
from ..security import roles_required

admin_bp = Blueprint("admin", __name__)


def _payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, description="A JSON object is required.")
    return data


def _decision_note(data, required=False):
    note = str(data.get("note", "")).strip()
    if required and not note:
        abort(422, description="A reason is required when rejecting an application or listing.")
    if len(note) > 500:
        abort(422, description="The decision note must be at most 500 characters.")
    return note or None


def _audit(action, resource_type, resource_id, details):
    db.session.add(AuditLog(
        actor_id=g.current_user.id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=json.dumps(details, separators=(",", ":")),
    ))


@admin_bp.get("/owner-applications")
@roles_required("ADMIN")
def list_owner_applications():
    status = request.args.get("status", "PENDING").upper()
    if status not in {"PENDING", "APPROVED", "REJECTED", "ALL"}:
        abort(400, description="Unsupported application status.")
    query = select(OwnerApplication).order_by(OwnerApplication.created_at.asc())
    if status != "ALL":
        query = query.where(OwnerApplication.status == status)
    applications = db.session.scalars(query.limit(100)).all()
    return jsonify({"items": [item.to_dict() | {"user_id": str(item.user_id)} for item in applications]})


@admin_bp.patch("/owner-applications/<uuid:application_id>/decision")
@roles_required("ADMIN")
def decide_owner_application(application_id):
    data = _payload()
    decision = str(data.get("decision", "")).upper()
    if decision not in {"APPROVE", "REJECT"}:
        abort(422, description="Decision must be APPROVE or REJECT.")
    note = _decision_note(data, required=decision == "REJECT")
    application = db.session.scalar(select(OwnerApplication).where(OwnerApplication.id == application_id).with_for_update())
    if application is None:
        abort(404)
    if application.status != "PENDING":
        abort(409, description="This application has already been reviewed.")
    user = db.session.scalar(select(User).where(User.id == application.user_id).with_for_update())
    if user is None or not user.is_active or user.role != "RENTER":
        abort(409, description="The applicant account is not eligible for approval.")

    previous = application.status
    application.status = "APPROVED" if decision == "APPROVE" else "REJECTED"
    application.decision_note = note
    application.reviewed_by = g.current_user.id
    application.reviewed_at = datetime.now(timezone.utc)
    if decision == "APPROVE":
        user.role = "OWNER"
        user.verification_status = "VERIFIED"
    _audit(f"OWNER_APPLICATION_{decision}D", "owner_application", application.id, {
        "user_id": str(user.id), "from_status": previous, "to_status": application.status, "note": note,
    })
    db.session.commit()
    return jsonify({"application": application.to_dict(), "user": user.to_dict()})


@admin_bp.get("/products/pending")
@roles_required("ADMIN")
def list_pending_products():
    products = db.session.scalars(select(Product).where(Product.status == "PENDING_REVIEW").order_by(Product.created_at.asc()).limit(100)).all()
    return jsonify({"items": [{
        "id": str(product.id),
        "owner_id": str(product.owner_id),
        "title": product.title,
        "description": product.description,
        "condition": product.condition,
        "locality": product.locality,
        "category": {"id": str(product.category.id), "name": product.category.name},
        "pricing": product.pricing.to_dict() if product.pricing else None,
    } for product in products]})


@admin_bp.patch("/products/<uuid:product_id>/decision")
@roles_required("ADMIN")
def decide_product(product_id):
    data = _payload()
    decision = str(data.get("decision", "")).upper()
    if decision not in {"APPROVE", "REJECT"}:
        abort(422, description="Decision must be APPROVE or REJECT.")
    note = _decision_note(data, required=decision == "REJECT")
    product = db.session.scalar(select(Product).where(Product.id == product_id).with_for_update())
    if product is None:
        abort(404)
    if product.status != "PENDING_REVIEW":
        abort(409, description="Only listings awaiting review can be moderated.")
    previous = product.status
    product.status = "ACTIVE" if decision == "APPROVE" else "REJECTED"
    _audit(f"PRODUCT_{decision}D", "product", product.id, {
        "owner_id": str(product.owner_id), "from_status": previous, "to_status": product.status, "note": note,
    })
    db.session.commit()
    return jsonify({"product": {"id": str(product.id), "status": product.status, "decision_note": note}})
