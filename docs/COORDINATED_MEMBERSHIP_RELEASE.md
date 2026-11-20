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


## Latest online-provider update

The subsequent update wires the supplied Stripe pricing table and the confirmed
modern PayPal monthly/yearly plans plus $60 hosted lifetime Buy Now into the
existing account checkout. See ONLINE_PAYMENT_SETUP.md for exact identifiers,
server-only settings, callbacks, cancellation behavior and launch verification.
The earlier statements that PayPal only supports monthly apply to the earlier
commit; new options are now implemented but remain disabled until configured.
The owner still needs the three Stripe Price IDs and private Stripe/PayPal
credentials/webhook settings. Cash App/Venmo remain unchanged. No production
merge, deployment, live purchase or secret update has been performed.


Online checkout validation before push: 249 backend tests passed (one opt-in PG-only
migration test skipped locally), 52 frontend tests passed and build passed. The
provider browser exercise passed Stripe account references and signed lifetime
fulfillment, PayPal yearly SDK binding with no access from browser approval alone,
and the $60 lifetime Buy Now/IPN flow; all external SDK/API calls were fixtures.
The existing three-plan Cash App/Venmo/gift/privacy browser test also passed.
The PostgreSQL CI job now includes all online payment tests. These results do not
replace the private provider settings or live merchant verification described in
ONLINE_PAYMENT_SETUP.md. No live funds were collected and billing flags stay off.


## Stripe Price IDs and current public embed settings

All three owner-confirmed Price IDs are now recorded as defaults (monthly
price_1UdJOJJLFxwakDjOkkkgfM7p, yearly price_1UdJi6JLFxwakDjOxl3QSEKa,
lifetime price_1UdJQnJLFxwakDjOdjVHLruu). Environment overrides remain supported.
STRIPE_PUBLISHABLE_KEY and STRIPE_PRICING_TABLE_ID can select the current public
embed without changing code. The newer supplied publishable key differs from the
original embed; matching account/table/secret configuration must be verified before
activation. Tests reject a secret key or test-mode key in the public-key field.
Latest local backend check: 254 passed, one opt-in PostgreSQL-only skip. Frontend
52 tests and build passed.

The preceding Firefox/WebKit run was cancelled during dependency installation on
a slow regional EC2 Ubuntu archive, before application tests ran. The workflow now
uses Ubuntu's official archive mirror, allows longer browser-download connections
and a 25-minute overall timeout. The real browser tests and all assertions remain
unchanged; no test failure is suppressed or bypassed by this setup fix.

## Final coordinated membership launch

The protected homepage now shows a Sign up and subscribe invitation while keeping
the approved artwork, room, portal and six feature cards. Active members do not
see this invitation; with MEMBERSHIP_REQUIRED=false the existing homepage stays
unchanged. Registration explains that the customer next logs in and chooses a
membership. Stripe and PayPal offer recurring subscriptions; Cash App and Venmo
remain available for owner-verified payments on all three existing plans. The
monthly manual plan explicitly says $5.99 for one calendar month, no ongoing
commitment and no automatic renewal. This does not mean free access.

Disabled online providers are visibly marked unavailable rather than silently
disappearing from the customer checkout. They cannot be used while disabled.
There are no free trials. Price, account binding, signed webhook verification,
refund handling and server-side membership enforcement remain unchanged.

Prepare every remaining change before ONE final Netlify production build:

1. Resolve the production owner mismatch: the Render account configuration
   currently returns accounts_configured=true but owner_ready=false, whereas the
   local setup found the owner. Privately compare the pooled URL, direct URL and
   DATABASE_NAMESPACE (default spiritual_vibz) between Render and local settings.
   Do not delete data, recreate schemas or change projects to hide the mismatch.
2. Confirm the live Stripe and PayPal account, plans, permissions and webhook
   configuration. Keep private credentials in the backend environment only.
3. Review the complete tested PR and obtain approval to merge and release.
4. Save the final backend configuration together, including
   MEMBERSHIP_REQUIRED=true and the verified provider flags. These flags are
   backend settings: changing them does not require rebuilding Netlify.
5. Deploy Render once from the final main commit. Check /api/health and
   /api/account/config: accounts_configured, owner_ready, required,
   stripe_enabled and paypal_api_enabled must be true before offering checkout.
   Verify support URL/email, authenticated owner access and historical data.
6. Deploy Netlify once from that same main commit, then verify signed-out signup,
   customer checkout, paid access, cancellation and provider webhook delivery.
   Real provider payments require a controlled owner-authorized transaction;
   fixtures are not proof of live merchant configuration. Do not promote before
   these checks pass. Stop Netlify builds afterward if desired to control credits.

This preparation branch explicitly skips Netlify review deployments. No production
environment settings, memberships, database records or artwork are changed by it.

## Checkout revisions after customer testing

The owner has deferred new Stripe checkout. Customer signup, homepage copy and
checkout no longer advertise Stripe or render its plan-selection button. Existing
Stripe receipt verification and authenticated cancellation remain intact for any
previous billing. STRIPE_CHECKOUT_ENABLED was set to false on Render; the MCP
environment update automatically redeployed the existing production commit. It
did not deploy the new frontend or the handle migration.

Remove the customer-facing "No free trials" wording without changing the actual
no-trial policy. PayPal plan buttons are "$5.99 monthly", "$45 yearly" and "Buy
lifetime access", with a separate "$60 once" lifetime heading. The provider SDK
still determines which PayPal/card funding methods a customer is eligible to use;
the application does not promise guest card availability.

Cash App and Venmo customers now enter their sender handle rather than finding a
transaction number. All three manual plans remain. The backend stores the handle
in a new additive sender_handle column and generates a separate request reference.
Handles may repeat for future renewals; only one pending request per account is
allowed. A handle never grants access. The owner independently verifies the sender,
amount and paid date/time, and supplies a unique receipt ID or stable receipt label
for approval. Handles alone and reused verified receipts are rejected. Old reference
submissions and historical records remain supported. Requests appear in the owner
dashboard; this change does not add payment-notification email delivery.

Deploy the backend before the handle form. PostgreSQL memberships_v4.sql and the
SQLite additive migration preserve existing rows. Neon runtime and direct URLs must
target the same endpoint/database before any migration can run; mismatched settings
now stop before schema writes rather than initializing a second database. Verify
Render login and startup before publishing the combined Netlify update once.
