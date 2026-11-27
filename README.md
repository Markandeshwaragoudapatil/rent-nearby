# RentNearby

**Rent what you need. Earn from what you own.**

A Bengaluru-first peer-to-peer rental marketplace. This repository is being built in phases; the current milestone is product definition and the responsive frontend foundation.

## Current status

- [x] Product brief and initial competitor scan
- [x] MVP scope, user journeys, architecture, ERD and API contract
- [x] React + Vite frontend foundation and responsive landing page
- [ ] Flask API, PostgreSQL models and migrations
- [ ] Authentication and role authorization
- [ ] Listings, availability and booking engine
- [ ] Payment provider integration (test mode only)

## Repository layout

```text
rentnearby/
├── frontend/       # React + Vite + Tailwind CSS
├── backend/        # Flask API (next implementation phase)
├── docs/           # PRD, architecture, data model, API and research
└── README.md
```

## Prerequisites

- Node.js 20.19+ or 22.12+
- npm 10+
- Python 3.11+
- PostgreSQL 15+ (needed when backend is introduced)

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Vite prints the local development URL (normally `http://localhost:5173`).

## Environment variables

Never commit credentials. The frontend currently uses local presentation data only. Backend and third-party environment variables will be documented when those integrations are implemented. A `.env.example` will contain names and safe placeholders only.

## Product and security principles

- Public listing data is separate from private user, booking and payment data.
- The backend is authoritative for prices, availability, permissions and booking transitions.
- Payment completion is verified server-side; frontend success screens are never proof of payment.
- Security deposits are tracked separately from platform revenue.
- No Aadhaar collection is planned for the MVP.
- Demo listings are clearly labelled and are not real inventory or evidence of demand.

## Research caveat

Competitor observations are based on public websites and materials linked in `docs/market-research.md`, accessed 27 November 2026. Publicly advertised metrics are not treated as independently verified.
