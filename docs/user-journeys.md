# User journeys

## Renter journey

1. Arrives on homepage and searches for a camera/projector/tool near a locality.
2. Browses approved listings and filters by dates, category and budget.
3. Opens a product, reviews condition photos, owner verification status, pickup locality, pricing and deposit.
4. Checks availability; API returns a server-calculated quote.
5. Signs in/registers and submits a booking request.
6. Receives owner decision; if accepted, pays within the displayed payment window.
7. Receives confirmed booking and coordinates pickup without public disclosure of the owner's exact address.
8. At handover, both parties confirm condition and OTP; booking becomes active.
9. Returns item; owner records return and condition.
10. Booking completes; renter may submit one review and report a dispute if needed.

## Owner journey

1. Registers and completes phone/email verification.
2. Creates listing with category, clear photos, condition, locality, rates, deposit and available dates.
3. Submits listing for moderation; can edit or pause it.
4. Receives booking request with dates and calculated earnings breakdown.
5. Accepts or rejects; acceptance creates a temporary reservation/payment deadline.
6. After verified payment, coordinates pickup and confirms handover.
7. Records return/condition and closes the rental.
8. Reviews earnings ledger and booking history; disputes are escalated to support.

## Admin journey

1. Signs in through a separately provisioned admin account.
2. Reviews listing queue and flags prohibited, misleading or unsafe products.
3. Approves/rejects listings with an auditable reason.
4. Monitors user reports, bookings, payment exceptions and disputes.
5. Suspends accounts or resolves disputes under documented policy.
6. Reviews marketplace health metrics and audit events.

## Key edge cases

- Product becomes unavailable between availability check and booking request.
- Two renters request overlapping dates concurrently.
- Owner accepts but renter payment expires or fails.
- Duplicate payment webhook arrives.
- User attempts to access another user's booking/listing/address.
- Listing is suspended while a future booking exists.
- Return is late, item condition differs, or either party raises a dispute.
