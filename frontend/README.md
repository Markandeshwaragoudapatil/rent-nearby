# RentNearby frontend

React + Vite + Tailwind CSS 4. Sample catalogue entries are development-only and clearly marked as demo content.

```bash
npm install
npm run dev
npm run build
npm test
```

Set `VITE_API_BASE_URL` in `.env.local` when the Flask API is available. Never place private credentials in Vite environment variables; all `VITE_` values are public in the browser bundle.
