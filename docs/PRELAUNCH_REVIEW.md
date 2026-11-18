# Spiritual Vibz prelaunch review

Review branch: `review/prelaunch-audit`, based on main
`7229f46a69926f88f7817440a270254d796c4b33`.
This is a review-only update. It does not authorize a production merge, deployment,
DNS change, change to login protection, or work on `neurospicymysticlandingpage`.

## Changes

1. `frontend/url-hygiene.js`, loaded before the app, removes only recognized
   attribution parameters (`utm_*`, click IDs and campaign tags). It uses
   `history.replaceState`, preserves history state, legitimate queries and the
   hash route and legitimate fragment query, and tolerates browsers that deny history access. It does
   not remove authentication `code`, `state`, application `date`, or `ref`.
2. Seven homepage PNGs have additional full-resolution, lossless WebP copies.
   All decoded RGBA pixels were compared with the sources during generation;
   dimensions, alpha, composition and colors are preserved. Original PNGs and
   all app icons remain intact. These copies total 9,949,354 bytes versus
   13,698,082 bytes (27.4% less). Five complete fonts have WOFF2 copies totaling
   436,644 bytes versus 1,300,104 (66.4% less); TTF fallbacks and licenses remain.
   The utility and byte inventory are committed. No production image service,
   new runtime dependency or paid service is required.
3. Browser artwork now uses the committed copies on Cloudflare, Netlify and
   Render instead of Netlify-only image URLs. Off-screen illustration sprites
   load lazily and decode asynchronously. The mobile tarot illustration has
   high fetch priority once eligible for loading, without loading its hidden
   desktop copy eagerly. Changed CSS/JS references have new cache versions.
4. Hash navigation compares normalized tool state, avoiding duplicate renders
   of the same route and handling malformed encoded hashes safely. Early focus/visibility
   events also wait until application state exists before refreshing the sky. API request
   timeouts use AbortController rather than the newer AbortSignal.timeout API.
5. Web Audio resumes suspended contexts for Safari, honors a volume of zero,
   closes contexts and oscillators on Stop/navigation/page exit, and prevents a
   pending resume from starting audio after Stop.
6. FastAPI and Cloudflare responses gain consistent nosniff, frame, referrer and
   browser-permission headers. API responses have `Cache-Control: no-store`.
   Netlify already has the same security headers. FastAPI now serves robots.txt
   and sitemap.xml as well as the new scripts. CORS/auth policy is preserved.
7. Canonical and sitemap continue to identify `https://app.neurospicymystic.com/`.
   Social previews use an existing landscape illustration, with dimensions and
   alt text. PWA/Apple/favicon metadata and icon files are preserved and tested.
8. Preserved and completed the previously requested **Your Metadata** work:
   Pythagorean name values, birth components, seven core numbers, master numbers,
   explicit per-letter vowel Y selection, Pinnacles, Challenges, actual reduction
   steps, missing values and an original in-depth symbolic reading. Browser and
   native UI use the same local Python calculation, chart, readable export and
   explicit Share/Journal actions. No web research, AI service, database write or
   personal example is required. Tests use a fictional name and date. This adds
   one tool to the **18 existing Explore tools**, bringing the total to 19.
9. Repaired CI's browser-script test loader after `frontend/package.json` became
   ESM for the Worker. The shipped classic scripts are tested through their real
   browser globals. Retained exact map distances, crossing geometry, complete
   sharing, rune uniqueness and binary-asset assertions. Ritual title tests now
   compare escaped labels in order. Browser tests open collapsed ritual/rune
   controls, use the current complete-reading Journal action and account for
   Metadata. Added real Firefox/WebKit compatibility CI, URL/audio/security/SEO
   tests and new script/optimized-asset checks in source/container smoke tests.
10. Netlify's ignore command cancels this specific review branch before building,
    including PRs targeting main. Other branches retain their build policy.
    Review commits carry `[skip netlify] [skip render]`; no deploy commands are
    run by the added workflows. GitHub Actions runs builds/tests only.

## Local verification

- Backend: 168 pytest cases and 28 legacy endpoint checks pass, including birth
  time/DST, natal positions, Moon calculations, asteroid reports, equinox dates,
  astrocartography geometry and new Metadata arithmetic/input validation.
- Browser libraries: 52 Node tests pass, including public asset/font references,
  original artwork parity, map math, readable complete sharing, rune casting,
  URL cleanup, Safari audio fallback and review deploy guard.
- Native: 43 UI tests, TypeScript, PNG validator/regressions and native-host audit
  pass. Android/iOS Metro JavaScript production bundles pass locally. The full
  APK/iOS simulator builds and asset-copy bundles run in GitHub Actions.
- Chromium browser evidence covers the six main tabs, all 18 existing Explore tools
  plus Metadata,
  complete readings, chart forms, calendars, tarot, quizzes, ritual library,
  shadow work, rune casting, Journal persistence and PNG sharing.
- Homepage layout checks include 320, 375, 390, 412, 430, 768, 959, 960, 1024,
  1280, 1440 and 1920px, portal scroll clearance and a 34px iPhone safe area.
- All 186 protected original PNG asset hashes match the previous approved set.
  Original fonts, native icons, homepage geometry, colors and navigation remain.
- Standalone Netlify static build passes locally; all 78 original tarot PNGs are
  copied. The complete source ZIP also starts successfully after extraction in a
  separate directory. These are local tests, not a Netlify/Render deployment or
  preview build.

## Hosting/security findings and manual checks

- Public DNS for `app.neurospicymystic.com` resolves to Cloudflare edge IPs.
  Main's check run identifies the `spiritual-vibez-app` Workers build, consistent
  with the existing Worker configuration and hosting documentation. Render's
  public origin responds 200 with the FastAPI app. This is evidence of the
  Cloudflare/Render path, **not confirmation of a switch to Netlify**. No DNS
  records, Worker routes or custom-domain attachments were changed.
- This environment receives Cloudflare error 1010/403 on the custom domain.
  Therefore public custom-domain API/SEO/social-crawler reachability must still
  be checked from an allowed browser/provider dashboard. Do not bypass its WAF.
- `https://spiritualvibz.netlify.app/` returns 401 and a Login Redirect document
  before app JavaScript runs. This is site access protection, not a calculator
  or frontend routing exception. No password protection or access controls were
  removed. An authorized Netlify owner should confirm the intended policy.
- Render's connected tool has no selected workspace. Its private service settings
  cannot be reviewed until the owner confirms the intended workspace. Repo
  configuration targets main; Render skip markers additionally protect review
  pushes. Existing PR check history shows Netlify previews but no Workers builds
  on those non-main commits; no Cloudflare settings were changed.
- Current FastAPI CORS permits all origins and credentials. Existing browser
  requests do not include cookie credentials. Tightening origins would change
  access policy, so it is a separate approval item: first confirm all real web,
  mobile and temporary host origins, then approve an explicit allowlist and
  credential policy. CORS is not authentication. Do not expose private APIs to
  work around the Netlify 401.
- The full browser suite runs in Chromium locally. Local Firefox launch is
  blocked by this container's read-only namespace/framebuffer restrictions;
  WebKit needs unavailable system libraries. Real Firefox/WebKit tests are
  included in GitHub Actions with their supported system dependencies and a
  virtual PulseAudio output, so audio assertions exercise real browser engines.
- Physical iPhone/iPad/Android Home Screen installation, OS share-sheet delivery
  and audible speaker/headphone output still require devices. Browser tests
  verify manifest/icon retrieval, real Web Audio context behavior and share-file
  generation; they cannot prove another app's handling of a shared attachment.
- Native Sound Frequencies still has its pre-existing educational screen without
  tone playback. This PR tests and fixes browser Play/Stop; it does not claim a
  native audio engine. Native ritual/search and the more extensive browser ritual
  library also retain their existing differences. No existing feature is removed.
- Country/history articles already marked as being researched remain unpublished.
  No new historical claims or copied third-party promotional material is added.
- Existing framework deprecation warnings remain (FastAPI startup events and
  test-client/pytest dependencies); they do not fail the tests.

## One manually approved release

**Do not release this PR until the owner explicitly approves.** First review its
GitHub checks and the manual items above, and verify the actual production service
and branch settings in the intended Render/Cloudflare workspaces.

After approval, use **one coordinated release of this reviewed commit** through
the existing main-connected pipeline. Do not also publish a ZIP, create a new
Netlify site, build a deploy preview or change DNS. The split hosting path needs
the Render backend and the existing Cloudflare frontend to consume the same
approved commit: the new Metadata endpoint cannot be supplied by a frontend-only
deployment. A single-service Render-only deployment would update the onrender.com
copy, but would not update independently hosted Cloudflare/Netlify static files.
Confirm those service settings before choosing manual versus automatic publishing;
do not claim that one frontend deploy updates the Python API.

Perform the approval/production merge/deployment in a subsequent task. This task
ends at the tested pull request. Keep the old live deployment until that approval.
