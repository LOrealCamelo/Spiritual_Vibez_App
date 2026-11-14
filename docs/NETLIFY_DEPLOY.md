# Spiritual Vibez: Netlify frontend + Render Python backend

This is an alternative to Cloudflare Workers. It does not require a Cloudflare
Worker to serve the app or forward the API. The existing Python FastAPI backend
stays on Render, and all eight existing API router families remain available.

## GitHub repository

https://github.com/LOrealCamelo/Spiritual_Vibez_App

## Netlify deployment

1. In the EXISTING Netlify account, choose **Add new project > Import an existing project**.
2. Connect the GitHub repository above.
3. Create a **new, separate** Netlify site for Spiritual Vibez. Do NOT modify the
   existing Netlify project hosting \`neurospicymystic.com\`.
4. Production branch: \`main\` (after this proposed change is merged).
5. Base directory: repository root (empty or \`.\`).
6. Build command: \`node frontend/scripts/build-netlify.mjs\`.
7. Publish directory: \`dist/netlify\`.
   These settings are in the repository's root \`netlify.toml\`.
8. First deploy to the temporary \`*.netlify.app\` hostname. Test the entire
   application there **before** changing custom-domain/DNS settings.

## How the app communicates

- When hosted on \`*.netlify.app\` or \`app.neurospicymystic.com\`, the
  browser fetches \`https://spiritual-vibez-app.onrender.com/api/*\` directly
  over HTTPS. The FastAPI backend already has CORS middleware; check browser
  network logs on the preview URL to confirm preflights and POST responses.
- Direct requests avoid Netlify's roughly 26-second external proxy timeout,
  which matters for some astrology calculations and for Render cold starts.
- \`/api/*\` on the Netlify domain is also available as a best-effort compatibility
  proxy, but the browser code does not rely on it.
- All 78 original tarot PNGs are copied at build time from
  \`mobile/assets/tarot\` to the public directory \`assets/tarot\`.
  Other illustrations/fonts/icons come from \`frontend/assets\` and do not
  require proxying through Render.
- Python serves all calculations; there are no Netlify Functions and no AI
  agent/Worker replacement of the backend.

## Verification before attaching the domain

1. Visit the temporary \`https://YOUR-SITE.netlify.app/\` and ensure the
   frontend HTML, styling, and artwork load.
2. Inspect browser Developer Tools > Network: requests for \`api/health\`,
   \`api/tarot/cards\`, and birthplace dropdown queries should reach
   \`spiritual-vibez-app.onrender.com\`, and return JSON.
3. Open \`/assets/tarot/00-the-fool.png\` on the new Netlify site: image must load.
4. Test a complete POST calculation for each relevant app feature (natal chart,
   moon calendar, numerology/synastry, spreads, divination, oracle, wellness,
   rituals, etc.). A successful health check alone does not prove the screens.
5. If browser CORS failures occur, fix the FastAPI allowed-origin policy and
   test OPTIONS/POST requests before using a redirect-only fallback.
6. Only after a successful preview, attach \`app.neurospicymystic.com\` to
   this new Netlify site and update any necessary DNS in the existing
   \`neurospicymystic.com\` zone; do not touch \`www\` or the apex records
   for the existing site.

Do not delete the current Cloudflare Worker or detach its custom hostname
before the Netlify preview works. An existing DNS/Worker route for
\`app.neurospicymystic.com\` may need to be removed as part of the final
switchover. That is an intentional separate step, not part of this change.
