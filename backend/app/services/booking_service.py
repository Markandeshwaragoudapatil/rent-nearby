from datetime import date, datetime, timedelta, timezone
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from ..models import AvailabilityBlock, Booking, BookingEvent, Product

RESERVED_STATUSES = ("ACCEPTED", "PAYMENT_PENDING", "CONFIRMED", "ACTIVE")

class BookingRuleError(Exception):
    def __init__(self, message, status_code=409):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def serialize_booking(booking):
    return {
        "id": str(booking.id),
        "product_id": str(booking.product_id),
        "renter_id": str(booking.renter_id),
        "start_date": booking.start_date.isoformat(),
        "end_date": booking.end_date.isoformat(),
        "rental_paise": booking.rental_paise,
        "deposit_paise": booking.deposit_paise,
        "fee_paise": booking.fee_paise,
        "total_paise": booking.total_paise,
        "status": booking.status,
        "payment_deadline_at": booking.payment_deadline_at.isoformat() if booking.payment_deadline_at else None,
        "created_at": booking.created_at.isoformat() if booking.created_at else None,
    }

def _expire_product_holds(product_id):
    now = datetime.now(timezone.utc)
    expired = db.session.scalars(
        select(Booking).where(
            Booking.product_id == product_id,
            Booking.status.in_(("ACCEPTED", "PAYMENT_PENDING")),
            Booking.payment_deadline_at.is_not(None),
            Booking.payment_deadline_at < now,
        ).with_for_update()
    ).all()
    for booking in expired:
        previous = booking.status
        booking.status = "CANCELLED"
        booking.payment_deadline_at = None
        db.session.add(BookingEvent(
            booking_id=booking.id, from_status=previous, to_status="CANCELLED",
            note="Payment hold expired automatically."
        ))

def _check_product_dates(product_id, start_date, end_date, exclude_booking_id=None):
    blocked = db.session.scalar(
        select(AvailabilityBlock.id).where(
            AvailabilityBlock.product_id == product_id,
            AvailabilityBlock.start_date < end_date,
            AvailabilityBlock.end_date > start_date,
        ).limit(1)
    )
    if blocked:
        raise BookingRuleError("The product is unavailable for the selected dates.")
    query = select(Booking.id).where(
        Booking.product_id == product_id,
        Booking.status.in_(RESERVED_STATUSES),
        Booking.start_date < end_date,
        Booking.end_date > start_date,
    )
    if exclude_booking_id:
        query = query.where(Booking.id != exclude_booking_id)
    if db.session.scalar(query.limit(1)):
        raise BookingRuleError("The selected dates overlap with an existing reservation.")

def request_booking(renter, product_id, start_date, end_date, idempotency_key=None):
    if not isinstance(start_date, date) or not isinstance(end_date, date):
        raise BookingRuleError("Dates must use YYYY-MM-DD format.", 422)
    if start_date < date.today() or end_date <= start_date:
        raise BookingRuleError("Choose a future start date and an end date after it.", 422)
    if (end_date - start_date).days > 90:
        raise BookingRuleError("A single rental request cannot exceed 90 days.", 422)
    if idempotency_key:
        existing = db.session.scalar(select(Booking).where(Booking.idempotency_key == idempotency_key))
        if existing:
            if existing.renter_id != renter.id:
                raise BookingRuleError("This idempotency key has already been used.", 409)
            return existing, False
    product = db.session.scalar(select(Product).where(Product.id == product_id).with_for_update())
    if product is None or product.status != "ACTIVE":
        raise BookingRuleError("Product not found or not available for rent.", 404)
    if product.owner_id == renter.id:
        raise BookingRuleError("You cannot rent your own product.", 403)
    if product.pricing is None or product.pricing.daily_price_paise <= 0:
        raise BookingRuleError("This product does not have a daily rental price.", 422)
    _expire_product_holds(product.id)
    _check_product_dates(product.id, start_date, end_date)
    rental = product.pricing.daily_price_paise * (end_date - start_date).days
    deposit = product.pricing.deposit_paise
    booking = Booking(
        renter_id=renter.id, product_id=product.id, start_date=start_date, end_date=end_date,
        rental_paise=rental, deposit_paise=deposit, fee_paise=0,
        total_paise=rental + deposit, status="PENDING", idempotency_key=idempotency_key,
    )
    db.session.add(booking)
    db.session.flush()
    db.session.add(BookingEvent(booking_id=booking.id, actor_id=renter.id, from_status=None, to_status="PENDING"))
    db.session.commit()
    return booking, True

def decide_booking(owner, booking_id, accept):
    booking = db.session.scalar(select(Booking).where(Booking.id == booking_id).with_for_update())
    if booking is None:
        raise BookingRuleError("Booking not found.", 404)
    product = db.session.scalar(select(Product).where(Product.id == booking.product_id).with_for_update())
    if product.owner_id != owner.id:
        raise BookingRuleError("You are not allowed to manage this booking.", 403)
    if booking.status != "PENDING":
        raise BookingRuleError("Only pending bookings can be accepted or rejected.")
    previous = booking.status
    if accept:
        _expire_product_holds(product.id)
        _check_product_dates(product.id, booking.start_date, booking.end_date, booking.id)
        booking.status = "ACCEPTED"
        booking.payment_deadline_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        note = "Owner accepted the request; payment is due within 30 minutes."
    else:
        booking.status = "REJECTED"
        note = "Owner rejected the request."
    db.session.add(BookingEvent(
        booking_id=booking.id, actor_id=owner.id, from_status=previous,
        to_status=booking.status, note=note
    ))
    try:
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()
        raise BookingRuleError("Another reservation already holds these dates.") from error
    return booking

def cancel_booking(renter, booking_id):
    booking = db.session.scalar(select(Booking).where(Booking.id == booking_id).with_for_update())
    if booking is None:
        raise BookingRuleError("Booking not found.", 404)
    if booking.renter_id != renter.id:
        raise BookingRuleError("You are not allowed to cancel this booking.", 403)
    if booking.status not in ("PENDING", "ACCEPTED", "PAYMENT_PENDING"):
        raise BookingRuleError("This booking can no longer be cancelled through this endpoint.")
    previous = booking.status
    booking.status = "CANCELLED"
    booking.payment_deadline_at = None
    db.session.add(BookingEvent(
        booking_id=booking.id, actor_id=renter.id, from_status=previous,
        to_status="CANCELLED", note="Cancelled by renter before payment confirmation."
    ))
    db.session.commit()
    return booking
