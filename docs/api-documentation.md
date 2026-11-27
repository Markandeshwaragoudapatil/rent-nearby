# RentNearby REST API

Base URL for local development: `http://localhost:5000/api/v1`

All request and response bodies use JSON unless otherwise stated. IDs are UUIDs. Prices are integer paise (₹1 = 100 paise). Cookie-authenticated requests must send credentials and a CSRF header on unsafe methods.

## Session and CSRF

Before the first POST/PATCH/PUT/DELETE request, call:

```http
GET /auth/csrf
```

Response:

```json
{ "csrf_token": "..." }
```

Keep the session cookie and send the token as `X-CSRFToken`. The React API client handles this bootstrap automatically and uses `credentials: "include"`.

## Implemented endpoints

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/health` | Public | API and database health |
| GET | `/categories` | Public | Active categories |
| GET | `/products` | Public | Active listings; supports `q`, `locality`, `category`, `page`, `per_page` |
| GET | `/products/{id}` | Public | Active product detail |
| GET | `/products/{id}/availability?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` | Public | Check blocked dates and reserved bookings |
| GET | `/auth/csrf` | Public | Create CSRF token |
| POST | `/auth/register` | Public + rate limit + CSRF | Register a RENTER account |
| POST | `/auth/login` | Public + rate limit + CSRF | Create session |
| POST | `/auth/logout` | Authenticated + CSRF | Clear session |
| GET | `/auth/me` | Authenticated | Current user |
| POST | `/owner/application` | Authenticated RENTER | Apply for owner access; does not grant the role immediately |
| GET | `/owner/application` | Authenticated | Read own owner application status |
| GET | `/owner/products` | OWNER | List own products |
| POST | `/owner/products` | OWNER | Create a DRAFT listing |
| POST | `/owner/products/{id}/submit` | OWNER | Submit a complete listing for moderation |
| GET | `/admin/owner-applications?status=PENDING` | ADMIN | List owner applications for review (`ALL`, `APPROVED`, `REJECTED` also supported) |
| PATCH | `/admin/owner-applications/{id}/decision` | ADMIN | Approve or reject an owner application |
| GET | `/admin/products/pending` | ADMIN | List submitted listings awaiting review |
| PATCH | `/admin/products/{id}/decision` | ADMIN | Approve or reject a listing |
| POST | `/bookings` | RENTER | Create a booking request |
| GET | `/bookings` | RENTER | List own booking requests |
| GET | `/bookings/{id}` | Booking participant or ADMIN | Read booking detail |
| POST | `/bookings/{id}/cancel` | RENTER | Cancel before payment confirmation |
| GET | `/owner/bookings` | OWNER | List requests for own products |
| POST | `/owner/bookings/{id}/accept` | Owner of product | Accept request and create a 30-minute payment hold |
| POST | `/owner/bookings/{id}/reject` | Owner of product | Reject pending request |
| POST | `/owner/products/{id}/availability-blocks` | OWNER of product | Block a date range |
| DELETE | `/owner/availability-blocks/{id}` | OWNER of product | Remove an availability block |

### Registration

```json
{
  "name": "Example Renter",
  "email": "renter@example.com",
  "password": "at-least-twelve-characters"
}
```

The server always assigns `RENTER`. Never send a role field or expect public registration to grant owner/admin permissions.

### Owner onboarding

A signed-in renter submits `POST /owner/application` with `business_name`, a 30–1500 character `description`, `contact_phone`, and `city`. The account remains a RENTER while the application is `PENDING`. Only an ADMIN can approve it; approval changes the account role to OWNER and sets `verification_status` to VERIFIED. A rejected application can be resubmitted after correcting the details. The MVP does not request Aadhaar or identity-document uploads.

Reject decisions require a reason. Admin decisions are written to `audit_logs`. The first administrator must be provisioned from a trusted server terminal after migrations: `flask --app run.py bootstrap-admin`. The command prompts for the name, email, and a hidden password; it refuses to run once an administrator exists. Do not expose this command as a public API.

An owner submits a completed draft using `POST /owner/products/{id}/submit`. The listing remains hidden until an administrator approves it, which changes its status to `ACTIVE`. Rejected listings can be corrected and resubmitted.

### Create booking request

```http
POST /bookings
Idempotency-Key: a-client-generated-unique-key
X-CSRFToken: ...
Content-Type: application/json
```

```json
{
  "product_id": "UUID",
  "start_date": "2030-01-10",
  "end_date": "2030-01-13"
}
```

The backend calculates the rental amount from the product's daily price and date range, adds the security deposit, and ignores any client-supplied price fields. The end date is exclusive (checkout); adjacent bookings are allowed.

New requests begin as `PENDING` and do not reserve inventory. The owner can accept one request. Acceptance is protected by a product row lock and a PostgreSQL partial GiST exclusion constraint. An accepted booking holds dates for 30 minutes while payment integration is pending.

Schedule this command every five minutes to release expired unpaid holds:

```bash
flask --app run.py expire-booking-holds
```

## Response and error format

Success examples:

```json
{ "user": { "id": "UUID", "name": "Example", "email": "renter@example.com", "role": "RENTER", "verification_status": "UNVERIFIED" } }
```

```json
{ "items": [], "page": 1, "per_page": 20, "total": 0 }
```

Errors use:

```json
{ "error": { "code": "CONFLICT", "message": "The selected dates overlap with an existing reservation." } }
```

Common status codes: 400 malformed request/CSRF, 401 unauthenticated, 403 forbidden, 404 not found/not visible, 409 booking or state conflict, 422 validation error, 429 rate limited, 500 unexpected server error. Internal stack traces are not returned.

## Planned but not implemented

- Profile and address management
- Email/phone verification and password reset
- Product image uploads (Cloudinary)
- Admin category management
- Razorpay order creation, payment signature verification and webhooks
- Transition from accepted/payment-pending to confirmed after verified payment
- Handover, return, damage evidence, reviews and disputes APIs
- Owner earnings ledger and platform commission accounting

Do not treat the presence of model tables as evidence that these workflows are available. No real payments should be accepted yet.
