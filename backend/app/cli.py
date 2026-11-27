import click
from datetime import datetime, timezone
from sqlalchemy import select
from .extensions import db
from .models import Booking, BookingEvent, Category

@click.command("seed-categories")
def seed_categories():
    initial = [
        ("Electronics", "electronics", "Cameras, audio and useful electronics."),
        ("Tools & Equipment", "tools-equipment", "Repair, cleaning and gardening tools."),
        ("Event Equipment", "event-equipment", "Projectors, speakers and event accessories."),
    ]
    for name, slug, description in initial:
        if not db.session.scalar(db.select(Category).where(Category.slug == slug)):
            db.session.add(Category(name=name, slug=slug, description=description))
    db.session.commit()
    click.echo("Default categories are ready.")

@click.command("expire-booking-holds")
def expire_booking_holds():
    now = datetime.now(timezone.utc)
    rows = db.session.scalars(
        select(Booking).where(
            Booking.status.in_(("ACCEPTED", "PAYMENT_PENDING")),
            Booking.payment_deadline_at.is_not(None),
            Booking.payment_deadline_at < now,
        ).with_for_update(skip_locked=True)
    ).all()
    for booking in rows:
        previous = booking.status
        booking.status = "CANCELLED"
        booking.payment_deadline_at = None
        db.session.add(BookingEvent(
            booking_id=booking.id, from_status=previous, to_status="CANCELLED",
            note="Payment hold expired automatically."
        ))
    db.session.commit()
    click.echo(f"Expired {len(rows)} unpaid booking hold(s).")

def register_commands(app):
    app.cli.add_command(seed_categories)
    app.cli.add_command(expire_booking_holds)
