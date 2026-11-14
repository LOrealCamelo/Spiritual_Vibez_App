# Cloudflare frontend + Render Python backend

Cloudflare Workers serves the static Spiritual Vibz frontend and forwards every /api/* request to the existing FastAPI service on Render. No Python calculation has been rewritten or replaced with a stub. This includes astrology, synastry, tarot, rituals, wellness, divination, oracle, and store routers, with their existing methods, payloads, status codes, and responses.

## Production origin

- Cloudflare frontend: https://app.neurospicymystic.com
- Python FastAPI origin: https://spiritual-vibez-app.onrender.com
- The Cloudflare Worker is defined by frontend/cloudflare-api.js, with frontend/wrangler.jsonc and run_worker_first for /api/* and /assets/tarot/*.
- All 78 original tarot PNGs are served from the existing Render FastAPI mount through Cloudflare; do not expect them under frontend/assets/.
- All location dropdowns use the original Python GeoNames dataset. Do not use the earlier separate offline CSC directory: its place_id values cannot be resolved by Python birth-chart services.
- The Worker sends no-store response headers for API calls, including user-entered birth data.

## Cloudflare Workers Builds

Use the existing Workers project associated with app.neurospicymystic.com, linked to this GitHub repository:

- Production branch: main
- Root directory: frontend
- Build command: npm install --no-audit --no-fund
- Deploy command: npx wrangler deploy
- Wrangler config: frontend/wrangler.jsonc, with main ./cloudflare-api.js and assets.directory .
- If Cloudflare has an explicit Workers custom domain/route configuration, keep app.neurospicymystic.com on this Worker so /api/* is handled by the same origin as the frontend.

The Render address is already the default in cloudflare-api.js. An optional trusted Worker environment variable PYTHON_API_ORIGIN can replace it if the service hostname changes. Do not put an API origin in user-controlled query parameters.

## Health and full backend verification (after deploying)

1. Open https://spiritual-vibez-app.onrender.com/api/health directly. Expect the JSON status online, not a Render 404/502.
2. Open https://app.neurospicymystic.com/api/health. Expect the same Python FastAPI health response, not the previous partial/501 Cloudflare stub.
3. Check https://app.neurospicymystic.com/api/astrology/locations/countries, regions?country=US, and cities?country=US&state=NY&query=Utica.
4. Check https://app.neurospicymystic.com/api/tarot/cards and /api/tarot/spreads. These must come from Python, not preview-only samples. Also open /assets/tarot/00-the-fool.png from the Cloudflare site; it must show the original tarot PNG.
5. In the app, check the actual workflows for natal charts, Moon phase, calendars, numerology, tarot cards/spreads, rituals, wellness, rune casts, pendulum, oracle, and store; GET-only checks are not enough for POST APIs.
6. Inspect browser Network responses for /api/*. Status 502 means the upstream is unreachable; 422 means Python received and rejected the submitted fields; 200 is transport success but the UI still needs an end-to-end check.

## Render

Retain the existing Python Web Service and its data files, Python requirements and configured start command. Do not shut Render down. Its free-tier cold starts may take longer than a static Cloudflare response; the frontend API request timeout is increased accordingly.

## Local tests

From frontend run npm test, or without installing dependencies run node --test tests/cloudflare-api.test.mjs. GitHub Actions runs these mocked proxy tests. Mock success does not verify live network reachability: confirm the URLs above after deployment.
