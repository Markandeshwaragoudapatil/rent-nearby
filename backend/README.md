# RentNearby backend

Flask API foundation with SQLAlchemy, PostgreSQL migrations, Argon2id password hashing, cookie sessions, CSRF protection, role-protected owner routes and a first transaction-safe booking workflow.

## Setup

Use Python 3.11+ and PostgreSQL 15+.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
flask --app run.py db upgrade
flask --app run.py seed-categories
flask --app run.py run --debug
```

The committed initial migration creates the schema and enables PostgreSQL's `btree_gist` extension. Its partial GiST exclusion constraint prevents overlapping `ACCEPTED`, `PAYMENT_PENDING`, `CONFIRMED` or `ACTIVE` bookings for the same product. Date ranges are half-open: the end date is checkout and is not occupied, so adjacent rentals are allowed.

SQLite is used only by the fast unit-test fixture. It does not enforce the PostgreSQL exclusion constraint; CI applies the migration against PostgreSQL.

## Implemented endpoints

- GET /api/v1/health
- GET /api/v1/categories
- GET /api/v1/products and GET /api/v1/products/{id}
- GET /api/v1/products/{id}/availability?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
- GET /api/v1/auth/csrf
- POST /api/v1/auth/register and /login
- POST /api/v1/auth/logout and GET /api/v1/auth/me
- GET/POST /api/v1/owner/products
- POST /api/v1/owner/products/{id}/submit
- POST /api/v1/bookings and GET /api/v1/bookings
- GET /api/v1/bookings/{id} and POST /api/v1/bookings/{id}/cancel
- GET /api/v1/owner/bookings
- POST /api/v1/owner/bookings/{id}/accept and /reject
- POST /api/v1/owner/products/{id}/availability-blocks
- DELETE /api/v1/owner/availability-blocks/{id}

Booking amounts are calculated by the server in paise using the daily price and rental duration. The client cannot submit its own price. Booking requests begin as PENDING and do not block inventory until the owner accepts. Acceptance creates a 30-minute payment hold. The platform fee is currently zero; commission assumptions are not yet validated and no payment is collected by this milestone.

## Expiring unpaid holds

Schedule this command every five minutes in the deployment environment:

```bash
flask --app run.py expire-booking-holds
```

The booking request and acceptance paths also expire stale holds for the affected product. A scheduler is still required so holds are released promptly when no new requests arrive.

## Security

Passwords are hashed with Argon2id. Unsafe browser requests are protected by CSRF; call GET /api/v1/auth/csrf and send the returned token in `X-CSRFToken` with the session cookie. Public registration always creates a RENTER. Owner role assignment is not self-service.

Production requires HTTPS, a strong random SECRET_KEY, a persistent rate-limit store and an explicit frontend origin. Production cookies use HttpOnly, Secure and SameSite=None for a cross-origin frontend/backend deployment. Confirm browser third-party-cookie behavior for the eventual deployment domains.

## Not implemented yet

Razorpay orders, server-side payment verification and webhooks; booking confirmation after payment; return/hand-over workflows; reviews and disputes APIs; image uploads; admin moderation; phone/identity verification and delivery integrations. Do not accept real payments or claim production readiness yet.
