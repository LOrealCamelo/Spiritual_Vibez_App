# Spiritual Vibz: Neon PostgreSQL setup and verification

## Current result

The existing FastAPI/vanilla-JavaScript application now supports Neon PostgreSQL.
It remains the same application; no Next.js replacement or demo was created.
The existing local SQLite mode remains available when `DATABASE_URL` is unset.
When PostgreSQL is configured, a connection failure never falls back to SQLite.

Target CLI context: organization `org-misty-dawn-94071509`, project
`shiny-dawn-67380861`, branch `production`, Postgres only. The CLI link is written
but could not be verified through the management API because account authorization
was not completed. The user-provided database endpoint was independently verified
with actual SQL and application tests.

## Tooling and provisioning results

- Installed `neon@9.6.2` globally under the writable workspace tool prefix.
- Initial `neon init -y --org-id org-misty-dawn-94071509 --project-id shiny-dawn-67380861 --branch production --services postgres`
  hit unwritable home-directory configuration/cache paths and a failed global
  coding-agent plugin installation.
- Retried with a private writable CLI config directory, writable npm cache and
  `--no-agent-setup`. Created the local link, `neon.ts` and npm dependencies.
- Installed the `neon` and `neon-postgres` agent skills project-locally and consulted
  them. No paid AI agents were run.
- `neon login` waited for browser authorization and timed out after 60 seconds.
  The user reported no browser window opened.
- `neon deploy` was attempted and failed with `Not signed in`. A PostgreSQL role
  password cannot authorize the Neon management API. No additional Neon services
  or paid resources were provisioned. The existing Postgres service was used.
- `neon.ts` loads successfully and declares no Auth, Functions, buckets, AI Gateway
  or Realtime service. PostgreSQL is included in every Neon branch.

To complete the management-CLI step, authorize `neon login` in the same workspace
/profile, then rerun the initialization/deploy commands. A login on an unrelated
personal computer does not authenticate this workspace. Never paste an API key,
password or connection URL into chat or source control.

## Runtime architecture

- Python uses `psycopg` 3 and a bounded connection pool (zero minimum, five maximum).
- `DATABASE_URL`: pooled application connection. Keep TLS enabled.
- `DATABASE_URL_UNPOOLED`: direct connection for versioned, additive schema setup.
- `DATABASE_NAMESPACE`: stable app schema prefix; default `spiritual_vibz`.
- Application traffic uses transaction-local search paths so Neon's transaction
  pooler cannot leak a previous request's account scope.
- Accounts, hashed sessions/reset codes, memberships, verified payment records,
  gift codes and audit/rate-limit records use the app membership schema.
- Saved server data uses account-specific schemas, preserving the existing
  per-account isolation. Unowned legacy data has a separate schema.
- Existing SQL repositories retain their interfaces through a small tested adapter.
  Membership write transactions preserve atomic redemption and payment approval.
- SQL definitions live in `backend/sql/*_v1.sql`; initialization creates missing
  tables/indexes and does not drop or overwrite existing app data.
- PostgreSQL failures return a generic 503 for API requests, without exposing
  connection details or silently selecting local files.

The real database now contains the empty app-owned schemas:

| Schema | Tables |
|---|---:|
| `spiritual_vibz_memberships` | 10 |
| `spiritual_vibz_legacy` | 7 |

No real administrator/customer was created by verification. Fake accounts and
payment records lived only in randomly named verification schemas, which were
removed afterward. Other projects and any existing application data were untouched.
Old SQLite files were retained; no automatic import was performed. Back up and plan
any legacy-data migration before activating the new datastore in production.
Browser-local journals/bookmarks keep their existing behavior; this update does
not silently upload them to Neon.

## Private environment and local commands

The supplied database credentials are saved in `.env.local`, mode 0600, and are
Git-ignored. Both pooled and unpooled values are private. The example file keeps
existing settings and adds placeholders only. Credentials never enter frontend
JavaScript or the static build.

The password was shared in chat. Rotate it in Neon after verification and replace
both private URL values before production use. Do not paste the replacement here.

Requirements: Node 24+, Python with `backend/requirements.txt` installed.

```sh
npm install
python -m pip install -r backend/requirements.txt
npm run build
npm test
npm start
```

`npm start` launches the existing FastAPI app using `.env.local` when present.
`PYTHON` can select an existing virtual-environment interpreter; `PORT`, `HOST`
and `SPIRITUAL_ENV_FILE` customize local startup. Render continues using its
existing Uvicorn/container startup and private environment settings.

## Verification evidence

Completed:

- `npm run build`: Neon configuration load, browser syntax and the existing static
  build passed; 25 top-level browser files and all 78 original tarot cards.
- `npm test`: 52 JavaScript tests passed.
- `python -m pytest backend/tests -q`: 206 tests passed, including PostgreSQL
  configuration/outage safety and refusal to run tests against an app database.
- Real Neon membership/PayPal suite: 29 tests passed in 340.56 seconds, including
  concurrent gift redemption, duplicate-payment protection, trial/renewal/
  cancellation/refund fixtures, account separation and session revocation.
- Real Neon endpoint script: all 28 endpoint checks passed.
- `python scripts/verify_neon.py --websocket --init-app`: launched the actual app
  with `npm start`; browser signup/login, owner-only approval, one-use gifts,
  private saves, logout, and responsive paid tools passed. An authenticated server
  journal entry and account/gift access survived an application restart.
- Inspection after cleanup found only the two app schemas above, with no remaining
  verification schemas.

This workspace's outbound TCP connections to Neon on port 5432 were closed. A
read-only HTTPS SQL check succeeded. For real application verification,
`--websocket` carried the PostgreSQL wire protocol inside certificate-verified
TLS WebSockets to Neon's actual pooled and unpooled endpoints, with loopback-only
local listeners. Production URLs retain their original TLS requirements and do
not use this verification transport. Direct TCP connectivity from Render remains
a production smoke check for the coordinated release.

Reproduce the secure verification transport only if needed:

```sh
python -m pip install -r frontend/tests/requirements.txt -r backend/tests/requirements-neon.txt
python scripts/verify_neon.py --websocket --backend-tests
```

`--init-app` additionally initializes the versioned empty app schemas if absent.
Verification creates and removes only its own isolated test schemas and never
submits a real payment. Without `--websocket`, verification uses normal TCP/TLS.

For isolated PostgreSQL pytest runs, supply `POSTGRES_TEST_URL` and optionally
`POSTGRES_TEST_URL_UNPOOLED`, leaving `DATABASE_URL` unset in the test process.
Pytest refuses collection if `DATABASE_URL` is already set, preventing accidental
writes to the application's real account schema.

An early browser test exposed account buttons accepting clicks during unfinished
network operations. Controls now stay disabled until the operation finishes;
the real-Neon browser flow passed after this fix. No approved artwork or layout
was changed.

## Hosting and billing remain unchanged

No Netlify/Render deployment, automatic-deploy change, DNS change or live billing
activation occurred. This branch is guarded against Netlify preview builds.

For a later coordinated release, configure the two database URLs privately on the
confirmed primary Render service. PostgreSQL replaces the requirement for local
membership database/user-directory paths. Preserve unrelated variables. Keep
`MEMBERSHIP_REQUIRED` and `PAYPAL_SUBSCRIPTIONS_ENABLED` off until the owner account,
notification delivery and live checkout/cancellation checks are ready.

The free Render backend's idle behavior and SMTP port restrictions still apply;
Neon solves persistent database storage, not server availability or email delivery.
Reconcile the newer Love experience already on GitHub main before combining this
branch with the existing membership/prelaunch work. No existing main-branch work
was overwritten or merged by this task.

## Files changed or added

- `.agents/skills/neon-postgres/SKILL.md`
- `.agents/skills/neon-postgres/references/branching.md`
- `.agents/skills/neon-postgres/references/egress-optimization.md`
- `.agents/skills/neon-postgres/references/full-text-search.md`
- `.agents/skills/neon-postgres/references/hybrid-search.md`
- `.agents/skills/neon-postgres/references/lakebase-search-drizzle.md`
- `.agents/skills/neon-postgres/references/vector-search.md`
- `.agents/skills/neon/SKILL.md`
- `.agents/skills/neon/references/auth.md`
- `.agents/skills/neon/references/claimable-neon.md`
- `.agents/skills/neon/references/function-triggers.md`
- `.agents/skills/neon/references/logs-loki.md`
- `.agents/skills/neon/references/parse-env.md`
- `.agents/skills/neon/references/sdk.md`
- `.env.example`
- `.gitignore`
- `backend/database.py`
- `backend/main.py`
- `backend/postgres.py`
- `backend/requirements.txt`
- `backend/routers/accounts.py`
- `backend/services/memberships.py`
- `backend/sql/memberships_v1.sql`
- `backend/sql/user_data_v1.sql`
- `backend/tests/conftest.py`
- `backend/tests/requirements-neon.txt`
- `backend/tests/test_postgres_adapter.py`
- `docs/MEMBERSHIP_LAUNCH.md`
- `docs/NEON_SETUP.md`
- `frontend/membership.js`
- `frontend/scripts/skip-review-deploy.mjs`
- `frontend/tests/deploy-guard.test.cjs`
- `neon.ts`
- `package-lock.json`
- `package.json`
- `scripts/build.mjs`
- `scripts/start.mjs`
- `scripts/verify_neon.py`
- `skills-lock.json`

Private `.env.local` and `.neon` context files are intentionally excluded from Git.
