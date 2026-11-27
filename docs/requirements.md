# RentNearby — Product Requirements Document

**Version:** 0.1 · **Date:** 27 November 2026 · **Launch geography:** Bengaluru, Karnataka

## 1. Product vision

Enable people to access useful products for short periods from nearby owners, while helping owners earn from underused assets. RentNearby is a two-sided marketplace; its initial differentiator is dependable local transactions rather than breadth of catalogue.

## 2. Problem and hypotheses

### Problems to validate
- Renters need occasional access to expensive or bulky items without buying them.
- Owners have idle assets but lack a trusted way to find renters and manage handovers.
- Existing rental options can be category-specific, vendor-operated, or designed around longer subscription periods.

### Hypotheses (not established facts)
- Bengaluru has sufficient concentrated demand and supply for camera/creator equipment, event AV equipment and selected tools.
- Renters will accept verified local pickup if the product is accurately described and handover is safe.
- Owners will list if onboarding is quick, booking rules are clear and damage/dispute handling is credible.

## 3. Target users

- Students and creators who need camera, audio or presentation equipment for short projects.
- Event organizers who need speakers, projectors and lighting.
- Households and hobbyists who need tools for occasional jobs.
- Individual owners and small specialist rental vendors.

## 4. MVP scope

### P0 — required for a controlled pilot
- Responsive public site, search and category browsing.
- Registration/login, email verification, secure sessions and role-aware access.
- Owner listing CRUD, image upload, pricing, location and availability.
- Product details with owner profile and transparent rental/deposit/fee breakdown.
- Booking request, owner accept/reject, renter cancellation under policy, booking history.
- Database-level prevention of overlapping active reservations.
- Admin listing moderation, user suspension and basic booking/dispute visibility.
- Audit trail for security-sensitive actions.
- Basic support/contact and policy pages.

### P1 — after pilot validation
- Razorpay test integration, server verification and signed webhooks.
- Verified handover OTP and before/after condition photos.
- Reviews restricted to completed bookings.
- Email notifications and owner response-time indicators.
- Location radius search and map display.

### Explicitly out of initial scope
- Delivery fleet, automated insurance, escrow claims, AI recommendations, native mobile apps, subscriptions, multi-city operations, Aadhaar storage and complex vendor accounting.

## 5. Core functional requirements

### Discovery
- Search by keyword; filter by category, daily price, date availability and locality.
- Product detail shows photos, condition, owner, pickup locality, rental unit, deposit and availability.
- Do not expose a private residential address before an accepted booking.

### Accounts and roles
- Roles: renter, owner and admin. A user may rent and own products; role is a capability, not a mutually exclusive account type. Admin is a separately granted privilege.
- Users can edit profile and manage saved addresses.
- Every private endpoint checks authenticated identity and resource ownership server-side.

### Listings
- Owner creates draft, submits for moderation, edits, pauses and archives own listings.
- Listing includes category, title, description, condition, locality, pricing, deposit, images and availability.
- Only approved and active listings appear in public search.

### Booking
- Dates are half-open intervals `[start, end)` in the product's local timezone; end must be after start.
- Request creates `PENDING`; owner may `ACCEPT` or `REJECT`.
- Acceptance creates a short payment window (`PAYMENT_PENDING`); expiry releases the reservation.
- Verified payment changes state to `CONFIRMED`; lifecycle advances to `ACTIVE`, then `COMPLETED`.
- Cancellation and dispute transitions follow server-side policy.
- Overlap is checked in a transaction and protected by a PostgreSQL exclusion constraint for blocking statuses.

### Trust and safety
- Owner identity/phone verification status is explicit and scoped; do not imply government-ID verification unless performed by a provider.
- Listing moderation and reporting.
- Handover evidence, booking event history and dispute records.
- Do not store card data or raw identity documents.

## 6. Non-functional requirements

- Mobile-first responsive UI; keyboard-accessible navigation and forms.
- WCAG 2.2 AA target for key flows.
- API validation, rate limits, CSRF protection for cookie auth, secure cookies in production, password hashing and least privilege.
- PostgreSQL transactions and concurrency-safe booking operations.
- Structured logs with secrets and personal data redacted.
- Automated unit/integration tests and migration checks.
- Clear loading, empty, error and success states.

## 7. Success metrics for pilot

Do not set arbitrary growth targets before baseline research. Instrument:
- Supply: approved active listings per pilot locality/category; owner activation rate.
- Demand: search-to-product-view, product-view-to-request and request-to-booking conversion.
- Marketplace quality: owner response time, acceptance rate, cancellation rate, completed rentals, repeat rentals.
- Trust: disputes per completed booking, damage claims, verification completion and support resolution time.
- Economics: gross booking value, platform revenue, payment costs, support/operations cost and contribution margin.

## 8. Validation plan

Before scaling, conduct 15–20 renter interviews and 10–15 owner interviews across two or three Bengaluru micro-markets. Ask about the last real occasion they rented/borrowed/bought an item, spend, urgency, trust concerns and current alternatives. Run a concierge pilot with a narrow catalogue. Do not interpret waitlist signups or synthetic website listings as validated demand.

## 9. Open decisions requiring founder approval

- Initial micro-markets and launch categories after interviews.
- Owner payout timing and payment-provider marketplace capability.
- Deposit collection/holding/refund mechanism and applicable legal/payment constraints.
- Cancellation, late return, damage and dispute policies.
- Whether pilot handover is owner-arranged pickup only.
- Legal entity, tax treatment, consumer/e-commerce obligations and privacy notice review.
