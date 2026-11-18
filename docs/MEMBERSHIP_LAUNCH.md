# Memberships, PayPal subscriptions and owner operations

This is the Spiritual Vibz **website and mobile Home Screen/PWA** flow. No App Store,
Stripe key or bank credential is embedded. PayPal hosted subscriptions support automatic monthly renewal; Cash App and Venmo remain manual. The separate
neurospicymysticlandingpage project must remain untouched.

## Review and activation

The implementation is on `feature/manual-memberships`, based on the tested
`review/prelaunch-audit` branch (PR #11). Review these changes separately. No
production merge, DNS change, provider deployment or resource purchase is authorized
by this guide. The gate is **off by default** so shipping/reviewing source alone does
not unexpectedly lock the existing app. Do not advertise paid access until the
backend's `MEMBERSHIP_REQUIRED=true` setup has passed the checks below.

Netlify hosts the frontend/sub-app at `app.neurospicymystic.com`; the repository
currently sends its API requests to `spiritual-vibez-app.onrender.com`. Keep that
existing connection. A static Netlify site cannot itself persist the Python
account database. Deploying frontend files alone does not activate memberships.

## Required backend setup — before taking payments

1. Confirm the actual Render service and its storage settings in the owner account.
   Use **durable private storage**, backed up before updates. Render persistent
   disks may require a paid service/plan; do not purchase or provision one without
   the owner's approval. If the current service has no durable storage, stop and
   approve a storage option first. Do not use `/tmp`, a build directory, the Git
   checkout or an ephemeral instance filesystem for customer accounts.
2. Configure private backend environment variables, for example with an approved
   persistent disk mounted at `/var/data`:

   ```text
   MEMBERSHIP_DB_PATH=/var/data/spiritual-memberships/accounts.db
   MEMBERSHIP_USER_DATA_DIR=/var/data/spiritual-memberships/private-users
   MEMBERSHIP_PUBLIC_URL=https://app.neurospicymystic.com
   MEMBERSHIP_SUPPORT_EMAIL=workwithloreal@gmail.com
   MEMBERSHIP_REQUIRED=false
   ```

   These are paths/public contact settings, not credentials. Actual disk mounting
   must be verified; merely setting a path does not make it persistent. The account
   store never falls back to temporary storage. Keep storage accessible only to
   the service. Database writes must use a **single service instance** with this
   SQLite design; do not horizontally scale it or copy a live DB with ordinary
   file-copy commands. Back up with SQLite's online backup mechanism and verify
   restoration, including all per-account data files.
3. In a **private server shell**, create the owner, using the same DB environment:

   ```sh
   python -m backend.scripts.create_owner --email workwithloreal@gmail.com
   ```

   The password is entered at hidden prompts, never in command arguments, source
   files, GitHub, chat or frontend environment variables. Existing addresses are
   not silently promoted or overwritten. Public registration can never create an
   administrator. Only the person controlling the private server can bootstrap
   an owner.
4. Deploy the reviewed frontend and backend together only after explicit approval.
   Log in as owner, test the dashboard, create a disposable customer, and verify
   both payment recipient profiles are the owner's intended **business** accounts.
   Cash App: `$lvcenterprise`; Venmo: `@lvcenterprise`. No provider account or payout
   eligibility was verified by code. Provider fees, holds and transfer timing still
   apply; this app cannot guarantee immediate bank availability.
5. Set `MEMBERSHIP_REQUIRED=true` on the correctly configured backend as the
   approved activation step. Restart it and verify an unauthenticated request to
   `/api/tarot/cards` returns 401; an unpaid account returns 403; a verified/gifted
   account succeeds. The public homepage, health and account entry points remain
   available. Never enable this flag against incomplete/ephemeral storage.
6. Verify register/login/logout/recovery, paid access, one-month/lifetime gifts,
   duplicate receipt rejection, expiration, data export and owner recovery before
   accepting real payments. Confirm HTTPS, Authorization CORS preflights from the
   actual Netlify/custom origin, browser storage behavior and phone layouts.

The separate bare React Native client remains a development client pointing at
local emulator APIs; this release does not publish a native app or add native
account screens. Do not repoint/distribute that client against a protected
production API until its native authentication flow is implemented. The supported
customer mobile experience here is the responsive website/PWA.

## What customers get

- Email/password account; passwords use salted PBKDF2-SHA256 with 600,000 iterations.
- Opaque 24-hour sessions. Only session hashes are stored on the server. Browser
  session tokens stay in sessionStorage, not URLs or long-lived localStorage.
  Closing the tab requires a fresh login; logout revokes the session server-side
  and reloads the page to discard in-memory personal forms/results.
- PayPal: a verified 24-hour free trial, then $5.99 USD monthly until cancelled.
  Cash App/Venmo: one manually verified calendar month, without automatic billing.
  Manual approval begins a new month at server time, or extends existing access
  from its current expiration. End-of-month dates clamp to the final
  valid day (January 31 to February 28/29). When PayPal is disabled, the account screen reminds active
  monthly customers within seven days of expiration; this is an in-app reminder,
  not a scheduled email or push notification service.
- Cash App/Venmo links and transaction-reference submission. A claim remains pending
  and grants **no access**. Only owner verification and approval changes membership.
  Lifetime customers are not prompted to renew or submit more payments.
- Private account-scoped browser saves and backend data, plus download of their own
  data even after membership expiration. Browser entries do not automatically sync
  to other devices. Logging in does not automatically claim pre-account entries.

The API enforces membership; hiding buttons is not the security boundary. Static
artwork, public homepage and shipped client/sample content are not DRM-protected.
Keep any future confidential premium books/articles on authenticated backend
endpoints rather than embedding them in public JavaScript.

## PayPal activation and cancellation

The owner supplied hosted button `QE2G8ZSPEMBBC`, merchant `M8B5TF7XNYV24`, and
receiving email `natture1st@gmail.com`, confirming $5.99 USD every month with a
24-hour trial. The integration requires that trial to be free; the verified signup
must contain `period1=1 D`, a zero trial amount, `period3=1 M`, a $5.99 regular
amount, USD, and recurring billing. A mismatched notification is rejected without
unlocking access. Confirm these exact terms in PayPal before launch.

After verifying durable storage and the owner login, configure server-only:

```text
PAYPAL_SUBSCRIPTIONS_ENABLED=true
PAYPAL_IPN_URL=https://spiritual-vibez-app.onrender.com/api/account/paypal/ipn
```

`MEMBERSHIP_REQUIRED=true` is also required; checkout cannot charge customers while
the app gate is disabled. In PayPal merchant settings enable IPN with the same
HTTPS notification URL. The checkout form sends an opaque account-bound `custom`
value. Do not use the bare static hosted button on the public sales page: it would
omit the account association. Use the authenticated checkout route.

Public SPA routes are `#sales`, `#register`, `#login`, `#checkout` and `#account`.
The existing homepage and six main navigation destinations remain intact.

Only an IPN round-trip returning `VERIFIED` from PayPal's fixed production HTTPS
endpoint can grant access. Browser return URLs never grant it. Trial coverage starts
at the verified subscription start, not at callback delivery time. Completed $5.99
payments grant coverage from their actual payment date; duplicate transaction IDs
cannot extend access again. Pending payments and sandbox events cannot unlock it.
Failed verification/storage requests return errors so PayPal can retry. Out-of-order
payment-before-signup also retries. No real subscription or charge was created in
automated tests.

Customers cancel in PayPal Automatic Payments using the in-app management link.
Cancellation is performed by PayPal, not a local switch pretending to stop charges.
Verified cancellation stops renewal status and preserves purchased/trial access
through its existing end date. Test the actual PayPal cancellation flow before
advertising the app. Full verified refunds/reversals remove the corresponding paid
coverage; partial refunds and other unsupported events require owner review.

A gift, account suspension or lifetime grant **does not cancel existing PayPal
billing**. Customers must cancel it in PayPal separately; the management link stays
available to lifetime members. Starting duplicate subscriptions at PayPal can create
duplicate charges; review the merchant subscription list and refund accidental
duplicates. Never approve a second subscription by email address alone.

The hosted button's real checkout, trial and renewal must be tested by the owner
with PayPal's tools/approved test setup. Production code deliberately rejects
sandbox IPNs. No payouts, instant-transfer eligibility, holds or fees are guaranteed.
No Stripe integration or API secret is configured by this update.

## Owner dashboard

Open **Account**, log in with the bootstrapped owner, and refresh the dashboard.
No customer can access these routes by changing frontend flags.

For each pending payment:

1. Open the actual Cash App or Venmo account independently.
2. Check that the recipient, customer, completed payment, currency and **$5.99**
   amount are correct. A screenshot, email, submitted identifier or pending transfer
   is not proof of receipt.
3. Approve and enter the verified transaction reference from that payment account,
   or reject with a reason. The backend prevents approving a request twice and
   reusing the same verified provider receipt for another membership.

The dashboard is the payment-request queue; refresh it to check for requests.
Automatic owner email alerts are not enabled by this implementation. Support uses
`workwithloreal@gmail.com`. Stripe recurring billing can be added later as a
separate server-side verified payment source; never put its secret key in browser
code or Netlify's public frontend build variables.

Generate a **new unique gift code for every recipient**:

- Choose one calendar month or lifetime access.
- Choose the redemption window (default 30 days, configurable up to 365).
- Copy the secret immediately and deliver it privately. Only its hash is stored;
  it cannot be retrieved later. Unused codes can be revoked.
- Each code is consumed atomically once, even if two accounts submit it at the
  same time. Redemption extends a monthly account or grants lifetime access.
- A lifetime grant has no membership expiration; its unused code can still expire.
- Gifts never enroll the customer in automatic billing.

You may suspend/restore customer access without deleting their saved records.
Suspension invalidates sessions. Owner accounts cannot be suspended through that
customer control. Approvals, gifts, recovery and access changes have audit records.

## Password recovery

Without SMTP, customers contact support. After independently verifying account
ownership, the logged-in owner can issue a single-use reset code in the dashboard
and deliver it privately. It expires after 30 minutes. Successful reset invalidates
all prior sessions. Never deliver a code solely because someone names an email.

Optional self-service reset emails use the owner's existing SMTP service with
certificate-verified STARTTLS. Configure server-only `SMTP_HOST`, `SMTP_PORT=587`,
`SMTP_USERNAME`, `SMTP_PASSWORD` and `SMTP_FROM`. A Gmail app password may require
Google account settings; never provide it through chat or commit it. No email
provider was connected, and delivery must be tested before announcing email recovery.

If the owner loses app access and SMTP is unavailable, use the authenticated private
server shell (not a public endpoint):

```sh
python -m backend.scripts.create_owner --email workwithloreal@gmail.com --recover
```

It issues a short-lived owner recovery code without promoting another account or
changing the password itself. Deliver/use that code privately. Do not run this
command in GitHub Actions or publish its output.

## Data preservation

Existing global legacy SQLite records are left intact and are never assigned to a
new customer. Authenticated feature requests use that account's private database
file; changing a request's user/session identifier cannot select another file.

Old `sv_private_journal`, mood and bookmark browser values remain untouched.
Account → Existing entries offers an explicit local copy only when those records
belong to the person using the device. It does not upload or delete originals.
Account data on a shared browser is not protection against somebody controlling
that browser/OS or developer tools; use trusted devices and sign out.

## Tests

`pytest -q backend/tests` includes membership authorization, untrusted payment
claims, duplicate verified receipts, simultaneous single-use redemption, expired
and revoked codes, private journals/exports, password reset/session revocation,
account suspension and rate limits. `frontend/tests/membership_flows.py` tests the
actual owner/customer browser journey and responsive layouts against temporary
storage. Existing tests run with enforcement off to check compatibility.

No real provider payments, email delivery, production storage restore or production
activation is performed by these tests. Those are owner-approved launch checks.
