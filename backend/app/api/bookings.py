from datetime import date
from uuid import UUID
from flask import Blueprint, abort, g, jsonify, request
from sqlalchemy import select
from ..extensions import db
from ..models import Booking, Product
from ..security import login_required, roles_required
from ..services.booking_service import (
    BookingRuleError, cancel_booking, decide_booking, request_booking, serialize_booking
)

bookings_bp = Blueprint("bookings", __name__)

def _date_value(value, field):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        abort(422, description=f"{field} must be a valid YYYY-MM-DD date.")

def _run(action):
    try:
        return action()
    except BookingRuleError as error:
        db.session.rollback()
        abort(error.status_code, description=error.message)

@bookings_bp.post("/bookings")
@roles_required("RENTER")
def create_booking():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, description="A JSON object is required.")
    try:
        product_id = UUID(str(data.get("product_id", "")))
    except (ValueError, TypeError, AttributeError):
        abort(422, description="product_id must be a valid UUID.")
    start_date = _date_value(data.get("start_date"), "start_date")
    end_date = _date_value(data.get("end_date"), "end_date")
    key = request.headers.get("Idempotency-Key")
    if key and len(key) > 100:
        abort(422, description="Idempotency-Key cannot exceed 100 characters.")
    booking, created = _run(lambda: request_booking(g.current_user, product_id, start_date, end_date, key))
    return jsonify({"booking": serialize_booking(booking)}), 201 if created else 200

@bookings_bp.get("/bookings")
@roles_required("RENTER")
def my_bookings():
    rows = db.session.scalars(
        select(Booking).where(Booking.renter_id == g.current_user.id).order_by(Booking.created_at.desc())
    ).all()
    return jsonify({"items": [serialize_booking(row) for row in rows]})

@bookings_bp.get("/bookings/<uuid:booking_id>")
@login_required
def booking_detail(booking_id):
    booking = db.session.get(Booking, booking_id)
    if booking is None:
        abort(404)
    product = db.session.get(Product, booking.product_id)
    if booking.renter_id != g.current_user.id and product.owner_id != g.current_user.id and g.current_user.role != "ADMIN":
        abort(403)
    return jsonify({"booking": serialize_booking(booking)})

@bookings_bp.post("/bookings/<uuid:booking_id>/cancel")
@roles_required("RENTER")
def cancel(booking_id):
    booking = _run(lambda: cancel_booking(g.current_user, booking_id))
    return jsonify({"booking": serialize_booking(booking)})

@bookings_bp.get("/owner/bookings")
@roles_required("OWNER")
def owner_bookings():
    product_ids = select(Product.id).where(Product.owner_id == g.current_user.id)
    rows = db.session.scalars(
        select(Booking).where(Booking.product_id.in_(product_ids)).order_by(Booking.created_at.desc())
    ).all()
    return jsonify({"items": [serialize_booking(row) for row in rows]})

@bookings_bp.post("/owner/bookings/<uuid:booking_id>/accept")
@roles_required("OWNER")
def accept(booking_id):
    booking = _run(lambda: decide_booking(g.current_user, booking_id, True))
    return jsonify({"booking": serialize_booking(booking)})

@bookings_bp.post("/owner/bookings/<uuid:booking_id>/reject")
@roles_required("OWNER")
def reject(booking_id):
    booking = _run(lambda: decide_booking(g.current_user, booking_id, False))
    return jsonify({"booking": serialize_booking(booking)})
