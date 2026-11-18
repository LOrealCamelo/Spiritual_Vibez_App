# Coordinated membership release — review only

This branch combines the prelaunch review, manual memberships, verified PayPal
subscriptions without a trial, and Neon persistence with main's newer Love UI.
It does not activate billing or authorize a production merge/deployment.
Existing draft PRs #11 and #12 are preserved; this consolidated PR contains their
work. Review and release this combined branch once rather than deploying each PR.

## Included work

- Sales, registration, login, account and checkout routes in the existing app.
- $5.99 USD monthly PayPal plan, button QE2G8ZSPEMBBC. Signup alone grants no
  access; only a verified completed payment activates a new paid subscription.
  Customers cancel automatic renewal through PayPal. Manual Cash App/Venmo
  payments require owner verification. Gift codes are single use.
- Neon PostgreSQL support for accounts, sessions, payments and private user data,
  retaining local SQLite support and all existing data. No automatic data import.
- The newer Love interface remains the only mounted questionnaire/finder. It uses
  authenticated requests, adds its result to the correct account journal, narrows
  city lists beyond 300 results, and displays the existing activity provider's
  results while retaining external search buttons. The older love.js source is
  retained but not loaded, avoiding duplicate controls/listeners.
- FastAPI explicitly serves the newer Love script/styles, matching Netlify.
- Prelaunch URL cleanup, local fonts and optimized copies of approved artwork,
  sharing/result formatting, audio and Metadata work are included. Original art,
  home layouts, portal, app icons and six-tab destinations remain present.
- The release branch is excluded by Netlify's existing pre-build review guard.
  No hosting deployment, environment update, live charge or real owner creation
  is performed by preparing/pushing this branch.

## Local verification

- Backend pytest: 214 passed (dependency/deprecation warnings only).
- Standalone API exercise: all 28 endpoint checks passed.
- Frontend Node tests: 52 passed.
- npm run build: passed, including the Postgres-only Neon configuration.
- Browser account flow: owner approval, register/login/logout, gifts, private
  journal isolation, paid tool access, authenticated Love locations and journal.
- Browser Love flow: real country/state/city dropdowns including Utica search,
  questionnaire/journal, fixture-based provider results, account routes, no JS
  errors or horizontal overflow at 320/375/390/430/1280/1440/1920px.
- Full browser regression: six tabs, 19 Explore routes, complete tarot spread,
  natal birth time/timezones, moon/calendar, asteroids, astrocartography, rituals,
  oracle, runes, Metadata, journal, PNG sharing, and audio Play/Stop.
- Home/portal/icon checks: original room, all six cards and original portal cards,
  safe-area navigation clearance, manifest/Apple touch/favicon assets; widths
  320/375/390/430/412/768/1024/1280/1440/1920 plus breakpoint checks.
- Existing native TypeScript and Jest: passed; 43 Jest tests.

Earlier Neon-specific verification is documented in NEON_SETUP.md. This release
has not revalidated credentials after the owner rotates the exposed password.
Current production connectivity, production CORS, email recovery delivery, actual
PayPal first payment/renewal/cancellation and physical device installation require
verification before public sales. Activity rendering uses a provider fixture in
browser tests; provider availability and event API credentials are separate checks.
GitHub Actions results are recorded on the consolidated pull request.

## Obtain a new local copy (PowerShell or Ubuntu)

Keep the old project folder. Clone into a different folder:

```sh
git clone --branch release/neon-memberships-review --single-branch https://github.com/LOrealCamelo/Spiritual_Vibez_App.git SpiritualVibz-release
cd SpiritualVibz-release
```

A clone contains source only: private environment files, passwords, installed
packages and saved production database contents are deliberately excluded.
Install Python requirements in a virtual environment and run npm ci if building.
Use the rotated Neon connection in a private .env.local file (never Git or chat).
The same DATABASE_URL must be configured on the Render backend for the account
created locally to be the account used in production.

With that file and backend dependencies ready, run with the virtualenv's Python:

```sh
python -m backend.scripts.create_owner --env-file .env.local --email workwithloreal@gmail.com
```

The command prompts twice for a 12–256 character password, never accepts it in
arguments, and refuses to overwrite/promote an existing address. Existing server
environment values take precedence over the optional local file. No account has
been created on the owner's behalf during this release preparation.

## One manually approved coordinated release

1. Review this PR and all CI results. Keep production auto-deploy/builds stopped;
   do not merge until the owner explicitly authorizes production release.
2. Rotate the exposed Neon password and configure Render's private DATABASE_URL.
   See NEON_SETUP.md for the direct migration URL, optional pool settings, and
   durable-storage checks. Do not put database credentials in Netlify browser code.
3. Confirm the public URL https://app.neurospicymystic.com, support email and IPN
   URL settings from MEMBERSHIP_LAUNCH.md. Keep MEMBERSHIP_REQUIRED and
   PAYPAL_SUBSCRIPTIONS_ENABLED false during setup.
4. Create/verify the owner in the same Neon database through the private command.
   Test account recovery; never use an ephemeral SQLite file for production.
5. With explicit release approval, merge the tested PR into main, then manually
   deploy the backend and frontend for the same reviewed commit. Do not enable
   preview deployments or deploy the separate landing-page project.
6. Confirm backend health, /api/account/config, owner login and frontend API/CORS
   connectivity. Enable PayPal IPN in the merchant account for
   https://spiritual-vibez-app.onrender.com/api/account/paypal/ipn.
7. Enable MEMBERSHIP_REQUIRED=true and PAYPAL_SUBSCRIPTIONS_ENABLED=true as the
   final approved activation. Restart the backend and verify the payment gate,
   verified first payment, replay protection, cancellation and access expiry.
   Browser return URLs alone must not unlock access. Do not advertise live sales
   until the complete customer flow passes.

A GitHub push/PR is not evidence that payments are enabled or production deployed.


## Added yearly and lifetime purchases (November 18)

The manual checkout now offers Monthly $5.99, Yearly $45.00 (saving $26.88
compared with twelve monthly payments), and Lifetime $60.00 once. Lifetime means
access while SpiritualVibz operates; no external provider subscription is created
or cancelled. All three plans use the existing Cash App/Venmo recipient profiles.
The signed-in customer chooses a plan and submits its payment reference. The
server records the plan and price, and the owner must independently verify the
exact amount and actual reference before approving. A request cannot grant access
itself or reuse an already verified receipt. Yearly renewal extends the existing
paid-through date by one calendar year, including leap-day clamping. Lifetime
removes the expiration requirement. Existing accounts, payments and gift codes
remain intact; additive v2 migrations label old payment requests as monthly $5.99.

PayPal remains $5.99 monthly. Yearly recurring PayPal and lifetime one-time PayPal
require separate hosted checkout configurations supplied by the owner; the monthly
button is never reused for another price. Existing PayPal subscribers must cancel
PayPal billing separately when purchasing manual yearly/lifetime access.

Updated local checks: 227 backend tests passed; the opt-in PostgreSQL-only test
is skipped in SQLite mode. All 52 frontend tests and npm run build pass. The
membership browser test now purchases all three plans, verifies their exact amounts,
checks yearly extension and lifetime status, and retains gift/privacy/logout flows.
A disposable PostgreSQL 17 GitHub Actions service exercises the real migration,
plan approvals, authentication, PayPal and gift tests without production secrets.
The live Neon check could not connect because the workspace's saved password is
no longer accepted. Configure the rotated pooled DATABASE_URL and direct
DATABASE_URL_UNPOOLED in Render and verify actual Neon connectivity before launch.
Do not post these URLs in chat, GitHub, or build logs. No production database or
hosting setting was changed to work around this verification blocker.
