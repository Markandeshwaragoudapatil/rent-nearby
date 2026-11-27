# REST API contract (planned)

Base path: `/api/v1`. JSON requests/responses. Cookie-authenticated routes require CSRF token on unsafe methods. All IDs are UUIDs. Paginated collections use `{ "items": [], "page": 1, "per_page": 20, "total": 0 }`.

## Public and authentication

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| GET | `/health` | Health check | Public |
| GET | `/categories` | Active categories | Public |
| GET | `/products` | Search/filter approved active listings | Public |
| GET | `/products/{id}` | Product details | Public |
| POST | `/auth/register` | Create account | Public + rate limit |
| POST | `/auth/login` | Create session | Public + rate limit + CSRF bootstrap |
| POST | `/auth/logout` | Revoke session | Authenticated |
| GET | `/auth/me` | Current user | Authenticated |
| POST | `/auth/verify-email` | Verify email token | Public, token-bound |
| POST | `/auth/forgot-password` | Request reset | Public + rate limit |
| POST | `/auth/reset-password` | Reset password | Public, token-bound |

## Profile and renter

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| PATCH | `/users/me` | Update profile | Authenticated self |
| GET/POST | `/users/me/addresses` | List/create addresses | Authenticated self |
| PATCH/DELETE | `/users/me/addresses/{id}` | Update/delete address | Owner of address |
| GET | `/users/me/bookings` | Renter booking history | Authenticated self |
| POST | `/products/{id}/availability-check` | Check date availability and quote | Public |
| POST | `/products/{id}/bookings` | Create booking request | Authenticated renter |
| GET | `/bookings/{id}` | Booking detail | Booking participant/admin |
| POST | `/bookings/{id}/cancel` | Request cancellation | Booking participant under policy |
| POST | `/bookings/{id}/reviews` | Review completed booking | Booking renter |
| GET/POST/DELETE | `/users/me/wishlist` | Manage saved products | Authenticated self |

## Owner

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| GET/POST | `/owner/products` | List/create own listings | Owner |
| GET/PATCH/DELETE | `/owner/products/{id}` | Read/update/archive own listing | Owner of listing |
| POST | `/owner/products/{id}/submit` | Submit for moderation | Owner of listing |
| POST | `/owner/products/{id}/availability` | Add availability/blackout rule | Owner of listing |
| GET | `/owner/bookings` | Requests and rental history | Owner |
| POST | `/owner/bookings/{id}/accept` | Accept request and create payment window | Owner of product |
| POST | `/owner/bookings/{id}/reject` | Reject request | Owner of product |
| POST | `/owner/bookings/{id}/handover` | Confirm handover with OTP/evidence | Owner of product |
| POST | `/owner/bookings/{id}/return` | Record return | Owner of product |
| GET | `/owner/earnings` | Earnings ledger (not deposits) | Owner |

## Payments and webhooks

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| POST | `/bookings/{id}/payment-order` | Create provider order for accepted booking | Booking renter |
| POST | `/payments/verify` | Verify checkout signature server-side | Booking renter; provider verification |
| POST | `/webhooks/razorpay` | Signed provider events; idempotent | Provider signature |

## Admin

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| GET | `/admin/overview` | Platform metrics | Admin |
| GET | `/admin/users` | Search users | Admin |
| POST | `/admin/users/{id}/suspend` | Suspend account | Admin |
| GET | `/admin/products/pending` | Moderation queue | Admin |
| POST | `/admin/products/{id}/approve` | Approve listing | Admin |
| POST | `/admin/products/{id}/reject` | Reject listing | Admin |
| GET | `/admin/bookings` | Booking oversight | Admin |
| GET | `/admin/disputes` | Dispute queue | Admin |
| POST | `/admin/disputes/{id}/resolve` | Record resolution | Admin |
| GET/POST/PATCH | `/admin/categories` | Category management | Admin |

## Error format

`{ "error": { "code": "VALIDATION_ERROR", "message": "Please correct the highlighted fields.", "fields": { "start_date": "Must be before end_date." }, "request_id": "..." } }`

Use appropriate HTTP status codes: 400 malformed input, 401 unauthenticated, 403 forbidden, 404 absent/not visible, 409 conflict (availability/state/idempotency), 422 validation, 429 rate limited, 500 generic internal error. Never return stack traces or secrets.
