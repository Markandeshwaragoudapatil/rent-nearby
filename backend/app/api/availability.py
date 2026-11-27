from datetime import date, datetime, timezone
from flask import Blueprint, abort, g, jsonify, request
from sqlalchemy import select
from ..extensions import db
from ..models import AvailabilityBlock, Booking, Product
from ..security import roles_required

availability_bp = Blueprint("availability", __name__)
RESERVED_STATUSES = ("ACCEPTED", "PAYMENT_PENDING", "CONFIRMED", "ACTIVE")

def parse_date(value, field):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        abort(422, description=f"{field} must be a valid YYYY-MM-DD date.")

@availability_bp.get("/products/<uuid:product_id>/availability")
def check_availability(product_id):
    start = parse_date(request.args.get("start_date"), "start_date")
    end = parse_date(request.args.get("end_date"), "end_date")
    if end <= start:
        abort(422, description="end_date must be after start_date.")
    product = db.session.get(Product, product_id)
    if product is None or product.status != "ACTIVE":
        abort(404)
    block = db.session.scalar(select(AvailabilityBlock.id).where(
        AvailabilityBlock.product_id == product_id,
        AvailabilityBlock.start_date < end,
        AvailabilityBlock.end_date > start,
    ).limit(1))
    reservation = db.session.scalar(select(Booking.id).where(
        Booking.product_id == product_id,
        Booking.status.in_(RESERVED_STATUSES),
        Booking.start_date < end,
        Booking.end_date > start,
    ).limit(1))
    return jsonify({"product_id": str(product_id), "start_date": start.isoformat(),
                    "end_date": end.isoformat(), "available": not block and not reservation})

@availability_bp.post("/owner/products/<uuid:product_id>/availability-blocks")
@roles_required("OWNER")
def create_block(product_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, description="A JSON object is required.")
    start = parse_date(data.get("start_date"), "start_date")
    end = parse_date(data.get("end_date"), "end_date")
    if start < date.today() or end <= start:
        abort(422, description="Choose a future start date and an end date after it.")
    product = db.session.scalar(select(Product).where(Product.id == product_id).with_for_update())
    if product is None or product.owner_id != g.current_user.id:
        abort(404)
    reservation = db.session.scalar(select(Booking.id).where(
        Booking.product_id == product_id,
        Booking.status.in_(RESERVED_STATUSES),
        Booking.start_date < end,
        Booking.end_date > start,
    ).limit(1))
    if reservation:
        abort(409, description="These dates already contain a reservation.")
    block = AvailabilityBlock(
        product_id=product_id, created_by=g.current_user.id,
        start_date=start, end_date=end,
        reason=str(data.get("reason", "")).strip()[:200] or None,
    )
    db.session.add(block)
    db.session.commit()
    return jsonify({"availability_block": {
        "id": str(block.id), "product_id": str(product_id),
        "start_date": start.isoformat(), "end_date": end.isoformat()
    }}), 201

@availability_bp.delete("/owner/availability-blocks/<uuid:block_id>")
@roles_required("OWNER")
def delete_block(block_id):
    block = db.session.get(AvailabilityBlock, block_id)
    if block is None:
        abort(404)
    product = db.session.scalar(select(Product).where(Product.id == block.product_id).with_for_update())
    if product is None or product.owner_id != g.current_user.id:
        abort(404)
    db.session.delete(block)
    db.session.commit()
    return jsonify({"message": "Availability block removed."})
