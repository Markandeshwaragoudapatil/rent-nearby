import re

import click
from datetime import datetime, timezone
from sqlalchemy import func, select

from .extensions import db
from .models import Booking, BookingEvent, Category, User
from .security import hash_password


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
    rows = db.session.scalars(select(Booking).where(
        Booking.status.in_(("ACCEPTED", "PAYMENT_PENDING")),
        Booking.payment_deadline_at.is_not(None),
        Booking.payment_deadline_at < now,
    ).with_for_update(skip_locked=True)).all()
    for booking in rows:
        previous = booking.status
        booking.status = "CANCELLED"
        booking.payment_deadline_at = None
        db.session.add(BookingEvent(booking_id=booking.id, from_status=previous, to_status="CANCELLED", note="Payment hold expired automatically."))
    db.session.commit()
    click.echo(f"Expired {len(rows)} unpaid booking hold(s).")


@click.command("bootstrap-admin")
@click.option("--name", prompt=True, help="Administrator's display name.")
@click.option("--email", prompt=True, help="Administrator's email address.")
def bootstrap_admin(name, email):
    """Create the first administrator from a trusted server terminal."""
    if db.session.scalar(select(User.id).where(User.role == "ADMIN")):
        raise click.ClickException("An administrator already exists; bootstrap is disabled.")
    name = name.strip()
    email = email.strip().lower()
    if not name or len(name) > 100:
        raise click.ClickException("Name must contain 1–100 characters.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise click.ClickException("Enter a valid email address.")
    if db.session.scalar(select(User.id).where(func.lower(User.email) == email)):
        raise click.ClickException("An account with this email already exists.")
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    try:
        password_hash = hash_password(password)
    except ValueError as error:
        raise click.ClickException(str(error)) from error
    administrator = User(name=name, email=email, password_hash=password_hash, role="ADMIN", verification_status="VERIFIED")
    db.session.add(administrator)
    db.session.commit()
    click.echo(f"Administrator account created for {email}.")


def register_commands(app):
    app.cli.add_command(seed_categories)
    app.cli.add_command(expire_booking_holds)
    app.cli.add_command(bootstrap_admin)
