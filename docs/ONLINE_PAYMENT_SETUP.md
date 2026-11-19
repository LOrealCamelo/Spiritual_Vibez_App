# Verified Stripe and PayPal checkout — configuration required before launch

This update stays inside the existing account/checkout flow and shared responsive
frontend. It does not enable production billing, merge the release branch, deploy,
create an administrator, change hosting/DNS or purchase any service. Cash App and
Venmo manual checkout and single-use gifts remain available as before.

## Confirmed public identifiers (not secret credentials)

| Access | Price | PayPal configuration |
| --- | --- | --- |
| Monthly | $5.99 USD, recurring monthly | P-49240117EJ7400837NL7FS3Q |
| Yearly | $45 USD, recurring yearly; save $26.88 versus 12 monthly payments | P-2CB49304GY501903DNL7FRPA |
| Lifetime | $60 USD once, while SpiritualVibz operates | Buy Now S6M5U5P48M76G |

There are no free trials. The supplied Stripe pricing table is
`prctbl_1UdJscJLFxwakDjONc9avp8H`; its supplied live publishable key is used only
in the browser component. The PayPal SDK is loaded once, rather than once per
button. PayPal's business SDK ID is the supplied public default; private server
settings can supply the matching REST-app client ID if the default SDK ID has no
associated REST secret. Never put a client secret in the SDK URL.

## Server environment (Render, not Netlify browser variables)

Keep checkout flags false during configuration/testing. Do not paste private
credentials in chat, GitHub or logs.

Stripe:

- `STRIPE_SECRET_KEY`: live secret key from the **same account** as the pricing table.
- `STRIPE_WEBHOOK_SECRET`: signing secret of the endpoint below.
- `STRIPE_MONTH_PRICE_ID`: the pricing table's $5.99 USD recurring-monthly Price ID.
- `STRIPE_YEAR_PRICE_ID`: $45 USD recurring-yearly Price ID.
- `STRIPE_LIFETIME_PRICE_ID`: $60 USD **one-time** Price ID.
- `STRIPE_CHECKOUT_ENABLED=true`: only after configuration and launch approval.

Price IDs start with `price_` and are public identifiers. They are not the product
IDs (`prod_`) or table ID. All three exact prices must be active/live, with quantity
one and no trial period. Disable free trials, adjustable quantities and discount
options in the pricing table; the verifier rejects trial subscriptions and
underpaid/unsupported invoices. Applicable tax can be additional to the approved
subtotal. Configure the table's after-payment redirect to
`https://app.neurospicymystic.com/#checkout`. Returning there never activates access.

Stripe webhook endpoint:
`https://spiritual-vibez-app.onrender.com/api/account/stripe/webhook`

Select `checkout.session.completed`, `checkout.session.async_payment_succeeded`,
`invoice.paid`, `customer.subscription.updated`, `customer.subscription.deleted`
and `charge.refunded`. Raw-body signatures are checked with Stripe's official
library (five-minute tolerance). The backend re-fetches Stripe resources using
fixed authenticated HTTPS endpoints and API version `2024-06-20`; this normalizes
resource shape independently of the webhook endpoint's event version. Unpaid
sessions cannot unlock access; an invoice arriving before its account-bound
checkout returns a retryable error. A paid invoice grants its verified period;
lifetime grants derive from a verified one-time receipt. Replay does not extend
coverage or revive a refunded receipt. The in-app Stripe cancellation button calls
the server for that account's subscriptions only, sets cancellation at period end,
and preserves paid access. Cancellation stays available when new checkout is off
as long as the Stripe secret key remains configured.

PayPal subscriptions:

- `PAYPAL_CLIENT_ID`: the public client ID of the live REST app used for SDK and API.
- `PAYPAL_CLIENT_SECRET`: that app's private secret.
- `PAYPAL_WEBHOOK_ID`: ID of the webhook configured on that same live app.

The REST app must be able to retrieve both supplied plan IDs. A secret belonging
to a different app may not have access to them; verify the matching app in PayPal
Developer rather than substituting unknown plans.
- `PAYPAL_API_ENABLED=true`: only after configuration and launch approval.

PayPal webhook endpoint:
`https://spiritual-vibez-app.onrender.com/api/account/paypal/webhook`

Select `BILLING.SUBSCRIPTION.ACTIVATED`, `BILLING.SUBSCRIPTION.UPDATED`,
`BILLING.SUBSCRIPTION.CANCELLED`, `BILLING.SUBSCRIPTION.SUSPENDED`,
`BILLING.SUBSCRIPTION.EXPIRED`, `PAYMENT.SALE.COMPLETED` and
`PAYMENT.SALE.REFUNDED`. The server verifies notifications through PayPal's fixed
live signature-verification API and re-fetches the subscription/plan. The plan
must have exactly one regular, indefinite monthly/yearly cycle at the approved
USD amount, without trials, setup fees or overridden terms. Browser `onApprove`
only binds/verifies the subscription; a separately verified completed sale grants
access. Actual recurring-sale resource formats must be verified with this merchant
configuration during the controlled launch checkout. The PayPal management link
lets customers cancel renewal in their own account. Verified cancellation keeps
already-paid access through its existing end date.

PayPal lifetime:

- Keep `PAYPAL_SUBSCRIPTIONS_ENABLED=true` for the existing verified classic IPN
  endpoint and legacy subscriptions.
- `PAYPAL_IPN_URL=https://spiritual-vibez-app.onrender.com/api/account/paypal/ipn`
- `PAYPAL_LIFETIME_ENABLED=true` only after launch approval and receiver checks.

The saved Buy Now button must charge $60 USD once to merchant M8B5TF7XNYV24,
receiving email natture1st@gmail.com, with no added shipping/unsupported fees.
The form adds an opaque account binding, secure return/cancel URLs and notify URL.
Only a verified completed $60 `web_accept` IPN unlocks lifetime access. Full
verified refunds/reversals revoke only that online receipt, preserving independent
manual/gift entitlements. The old monthly hosted button QE2G8ZSPEMBBC remains a
fallback/legacy route; the new SDK monthly/yearly choices replace its visible
monthly button when modern PayPal is enabled.

## Data, safety and pending verification

Additive migration `memberships_v3.sql` creates account-bound online checkouts,
subscriptions and receipts. No user, manual payment or gift is deleted. Automatic
receipts extend derived access independently of manual grants, allowing a full
refund to remove only its own coverage. Duplicate automatic subscriptions are
blocked across the legacy PayPal, modern PayPal and Stripe paths. Manual purchases
never cancel provider billing. Review any existing recurring agreements before
switching payment methods; provider periods start at checkout and can overlap
remaining manual paid time. Partial refunds, credit-balance adjustments and unusual
provider disputes require owner review rather than guessed access changes.

The saved workspace Neon password was rejected after rotation. Configure both
rotated pooled `DATABASE_URL` and direct `DATABASE_URL_UNPOOLED` in Render and
verify live connectivity before activating payments. The GitHub disposable
PostgreSQL tests do not prove current Neon credentials or live provider settings.

Tests use real signature checking and the actual account/callback routes, with
provider APIs and browser SDKs replaced by fixtures. They do not charge a customer,
verify the real merchant's private API credentials, prove live webhooks arrive,
or test real mobile payment-app handoffs. Before promotion, perform an explicitly
approved controlled checkout, renewal/cancellation and refund verification on the
same deployed frontend/backend commit. Keep all flags off until those settings
are ready. Do not use a browser approval alert, URL parameter or an unverified
subscription ID as evidence that access should be granted.
