# RentNearby backend

Flask API foundation using SQLAlchemy, Flask-Migrate, Argon2id password hashing, server-side session authentication, CSRF protection and role-protected owner listing routes.

## Setup

Use Python 3.11+ and PostgreSQL 15+ for persistent development.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
flask --app run.py db init
flask --app run.py db migrate -m "Initial schema"
flask --app run.py db upgrade
flask --app run.py seed-categories
flask --app run.py run --debug
```

For a local smoke test without DATABASE_URL, the API uses SQLite. SQLite is not production-ready and does not enforce PostgreSQL-specific booking constraints.

## Implemented endpoints

- GET /api/v1/health
- GET /api/v1/categories
- GET /api/v1/products and GET /api/v1/products/{id}
- GET /api/v1/auth/csrf
- POST /api/v1/auth/register and /login
- POST /api/v1/auth/logout and GET /api/v1/auth/me
- GET/POST /api/v1/owner/products
- POST /api/v1/owner/products/{id}/submit

Registration always creates a RENTER, ignoring client-supplied roles. Owner routes require the OWNER role; owner role assignment is intentionally not self-service. Listings are initially DRAFT and only ACTIVE products appear in public catalogue queries.

## Security

Passwords are hashed with Argon2id. Sessions use HttpOnly cookies; unsafe browser requests are CSRF protected. Production requires HTTPS, a strong random SECRET_KEY, an explicit frontend origin and persistent rate-limit storage. Review cookie and CORS configuration before deployment.

## Not implemented yet

Image uploads, admin moderation, availability calendars, the booking service, PostgreSQL overlap exclusion migration, Razorpay orders/webhooks and email verification are later milestones. The current model contains booking/payment foundations only; do not accept real bookings or payments yet.
