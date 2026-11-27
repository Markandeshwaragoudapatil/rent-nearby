# RentNearby

**Rent what you need. Earn from what you own.**

A Bengaluru-first peer-to-peer rental marketplace connecting people who own useful products with neighbours who need them temporarily.

## Current development status

- [x] Product brief, MVP scope, user journeys, architecture, ERD and initial competitor research
- [x] Responsive React + Vite landing page and clearly labelled demo catalogue
- [x] Flask API foundation, SQLAlchemy models and PostgreSQL Alembic migration
- [x] Cookie-session authentication, Argon2id password hashing, CSRF and role checks
- [x] Product catalogue and owner listing foundation
- [x] Availability blocks and booking request/accept/reject workflow
- [x] PostgreSQL exclusion constraint preventing overlapping reserved rentals
- [x] React renter registration/login connected to Flask sessions
- [x] Public browse and product-detail pages connected to the live catalogue API, with an explicitly labelled demo fallback
- [x] Backend and frontend GitHub Actions checks
- [x] Owner application, admin approval and listing moderation APIs with audit logs
- [ ] Cloudinary product image uploads
- [ ] Razorpay test-mode order creation, verification and signed webhooks
- [ ] Payment-confirmed booking, handover, return and dispute workflows
- [ ] Production deployment and end-to-end browser testing

This is a development MVP, not yet a live marketplace. Demo listings are not real inventory. No real payments are enabled.

## Repository layout

```text
rent-nearby/
├── frontend/       # React + Vite + Tailwind CSS 4
├── backend/        # Flask REST API, SQLAlchemy and migrations
├── docs/           # Product, architecture, data model and API documentation
└── .github/
    └── workflows/  # Backend PostgreSQL and frontend CI checks
```

## Prerequisites

- Node.js 22 (or 20.19+)
- npm 10+
- Python 3.11+
- PostgreSQL 15+ (CI currently verifies against PostgreSQL 16)

## Run the frontend

```bash
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

Set `VITE_API_BASE_URL=http://localhost:5000/api/v1` in `.env.local`.

## Run the backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set a local PostgreSQL connection string in `.env`, then run:

```powershell
flask --app run.py db upgrade
flask --app run.py seed-categories
flask --app run.py run --debug
```

The frontend and backend both run locally; the frontend API client includes session cookies and CSRF tokens automatically.

## Tests

Backend (run from `backend/`):

```bash
pytest -q
```

Frontend (run from `frontend/`):

```bash
npm ci
npm run test
npm run build
```

GitHub Actions runs backend tests against PostgreSQL 16, verifies the exclusion constraint, and runs frontend tests/build on relevant pull requests and feature branch pushes.

## Admin bootstrap

After applying migrations, provision the first administrator from a trusted backend terminal:

```bash
flask --app run.py bootstrap-admin
```

The command prompts for the administrator details and a hidden password. It refuses to create another administrator after the first one exists. Public registration cannot grant ADMIN or OWNER roles.

## Booking integrity

Rental dates use half-open ranges: `[start_date, end_date)`. The PostgreSQL partial GiST exclusion constraint prevents overlapping `ACCEPTED`, `PAYMENT_PENDING`, `CONFIRMED` and `ACTIVE` bookings for the same product. Owners' accepted requests have a 30-minute payment hold; schedule the backend command `flask --app run.py expire-booking-holds` every five minutes.

## Security and product principles

- Backend is authoritative for prices, availability, permissions and booking transitions.
- Public registration always creates a RENTER; client input cannot grant OWNER or ADMIN access.
- Passwords use Argon2id; unsafe browser requests use CSRF tokens.
- Production requires HTTPS, a strong `SECRET_KEY`, explicit CORS origins and persistent rate-limit storage.
- Payment completion must be verified server-side; frontend success screens are never proof of payment.
- Security deposits are tracked separately from platform revenue.
- No Aadhaar collection is planned for the MVP.
- Never commit secrets; Vite `VITE_*` variables are public in the browser bundle.

## Next milestones

1. Complete product editing and image uploads.
3. Razorpay test integration with idempotent webhooks.
4. Payment-confirmed booking transitions and return/handover workflow.
5. End-to-end tests, deployment hardening and pilot readiness.

See [API documentation](docs/api-documentation.md), [database design](docs/database-design.md), [architecture](docs/architecture.md) and [implementation plan](docs/implementation-plan.md).
