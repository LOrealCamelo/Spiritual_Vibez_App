# Cloudflare backend migration — phase 1

This branch adds a Cloudflare Worker for the birth country, state/province, city and IANA timezone selectors. It keeps the currently working static HTML/CSS/JS frontend. The Python calculation backend is **not** yet migrated.

## Cloudflare Workers Builds settings after merging

- Production branch: `main`
- Root directory: `frontend`
- Build command: `npm install --no-audit --no-fund && npm run build:geo`
- Deploy command: `npx wrangler deploy`

The pinned Wrangler config (`wrangler.jsonc`) defines `spiritual-vibez-app` and compatibility date `2026-11-14`. The build creates static `geo/` assets by country using MIT-licensed countries-states-cities-service and CC0 tz-lookup. No runtime location API key is required and no birth data is sent to third-party geocoding services. Timezone lookups are approximate near geographic borders.

After deploying, test:
- `/api/health`
- `/api/astrology/locations/countries`
- `/api/astrology/locations/regions?country=US`
- `/api/astrology/locations/cities?country=US&state=NY&query=Utica`

The frontend's existing `/api/astrology/natal-chart`, other ephemeris, journals, and tarot routes still require a Cloudflare-native implementation and respond with HTTP 501. Do not retire Render until migration and persistence are completed.

## Local tests

Run `npm install`, `npm run build:geo` and `npm test` from `frontend`.
