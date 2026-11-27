# RentNearby frontend

React 19 + Vite 7 + Tailwind CSS 4. Sample catalogue entries are development-only and clearly marked as demo content.

## Setup

```bash
npm ci
cp .env.example .env.local
npm run dev
```

Set `VITE_API_BASE_URL=http://localhost:5000/api/v1` in `.env.local`. Start the Flask API separately from the `backend/` directory. The API client sends cookies with `credentials: include`, obtains CSRF tokens from `/auth/csrf`, and sends `X-CSRFToken` on unsafe requests.

## Implemented frontend workflows

- Public homepage and demo-only browse/product preview.
- Renter registration and login connected to Flask session authentication.
- Authenticated account page and logout.
- Protected owner route (available only when the backend account role is OWNER).
- Public registration always creates a RENTER. The frontend does not offer role escalation or self-service owner privileges.

## Commands

```bash
npm run dev
npm run test
npm run build
npm run preview
```

## Environment and security

Only public configuration belongs in Vite environment variables. Every `VITE_` value is embedded in the browser bundle; never put database credentials, session secrets, payment secrets or private API keys there.

For local development, use the same host name for frontend and backend (for example, `localhost`) and configure Flask CORS to allow the frontend origin with credentials. Production must use HTTPS, a strong backend `SECRET_KEY`, secure cookies and a persistent rate-limit store.
