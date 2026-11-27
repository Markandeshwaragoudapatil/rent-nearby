# Implementation roadmap

The eight-week estimate is a planning hypothesis, not a commitment; timing depends on scope decisions, integrations and testing access.

| Milestone | Work | Exit criteria |
|---|---|---|
| 1. Discovery and product definition | Market scan, interviews, PRD, user journeys, data model, API contract, design system | Founder reviews scope, pilot segment and high-risk policy decisions |
| 2. Frontend foundation | React/Vite/Tailwind, routing, responsive public pages, browse and product preview | Production build passes; responsive and accessibility smoke tests pass |
| 3. Backend foundation | Flask factory, config, SQLAlchemy, PostgreSQL, migrations, auth/session/CSRF | Migration clean; auth and role-isolation tests pass |
| 4. Listings | Categories, owner CRUD, signed image upload, moderation, search/filter | Only approved listings public; owner cannot mutate another owner's listing |
| 5. Booking engine | Date availability, quote calculation, state machine, transactions, exclusion constraint | Concurrent overlapping reservation test proves one winner only |
| 6. Payments | Razorpay test orders, signature verification, webhook idempotency, ledger | Duplicate/invalid webhook and failed-payment tests pass |
| 7. Trust/admin | Handover OTP, condition evidence, reports, disputes, admin tools | Sensitive actions audited; dispute path tested |
| 8. Hardening and pilot | Security review, responsive QA, observability, backup/restore, deployment | Release checklist signed off; no unresolved critical/high findings |

## Current implementation notes

- Milestone 1 documentation is present in `docs/`.
- Milestone 2 has a first responsive landing page, browse preview, sample product detail and navigation states.
- Preview catalogue records use `demo-` IDs and explicit labels; no live booking or payment claims are made.
- Dependency installation and Vite build could not yet be verified in this execution environment because npm registry installation attempts timed out. Re-run `npm install`, `npm run build` and `npm test` in a network-enabled environment before treating the frontend as runnable.
