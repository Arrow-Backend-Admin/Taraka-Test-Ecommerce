# Razorpay test-mode runbook

This is the human procedure for proving the payment path with **real Razorpay
test-mode infrastructure**. It has not been executed yet. Until it is, every row
below is UNVERIFIED and the payment integration must not be described as
production-ready.

Scope: one successful test payment, one failed payment, and one replayed webhook.
Do not use live keys. Do not run this against real customer data.

## 0. Preconditions

- [ ] A Razorpay account with test-mode access.
- [ ] Test keys from Dashboard → Account & Settings → API Keys. They start with
      `rzp_test_`. Live keys start with `rzp_live_` and are refused outside
      production.
- [ ] A public HTTPS tunnel to the local API (see step 2).
- [ ] The API running with `RAZORPAY_MOCK=false` and the test keys in the
      environment (never in a commit).
- [ ] `APP_ENV=development` (or `staging`) for this drill.
- [ ] A product with stock so checkout can create an order.

Start the stack:

```bash
cd apps/api
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
# repo root, another terminal
npm run dev
```

## 1. Configure test keys

Put these in `apps/api/.env` (ignored by git) or the process environment:

```dotenv
APP_ENV=development
RAZORPAY_MOCK=false
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=<a long random string you also paste into Razorpay>
STOREFRONT_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000
```

`RAZORPAY_WEBHOOK_SECRET` is a secret **you** choose and register in the
dashboard. It is not the API key secret.

Confirm the app starts. A test key outside production is allowed; a live key
outside production is refused at startup.

## 2. Open a tunnel

Razorpay must reach the API over HTTPS. Any tunnel works; this example uses
Cloudflare Tunnel because it needs no account for a quick tunnel.

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Copy the `https://<random>.trycloudflare.com` URL. The webhook endpoint is:

```text
https://<random>.trycloudflare.com/webhooks/razorpay
```

Keep the tunnel running for the whole drill. If it restarts, the hostname
changes and the webhook registration must be updated.

Alternatives: `ngrok http 8000`, or a deployed staging URL. Record which one was
used.

## 3. Register the webhook

Razorpay Dashboard → Account & Settings → Webhooks → Add New Webhook.

- **URL:** the tunnel URL plus `/webhooks/razorpay`.
- **Secret:** the same `RAZORPAY_WEBHOOK_SECRET` from step 1.
- **Active events:** at minimum
  - `payment.captured`
  - `payment.failed`
  - `order.paid`
  - `refund.processed`
- **Alert email:** an address a human reads.

Send a test event from the dashboard if offered, and confirm a row appears in
`webhook_events` with a valid signature. If it does not, see
`docs/runbooks/failing-webhooks.md`.

## 4. One successful test payment

1. Browse the storefront, choose an available size, add to cart.
2. Go to `/checkout`, fill the form with test data.
3. Click **Create order and pay**. Razorpay Checkout opens.
4. Pay with a Razorpay test method. Card `4111 1111 1111 1111`, any future
   expiry, any CVV is the usual test card; UPI test handles are listed in the
   Razorpay test documentation. Use whatever the dashboard currently documents.
5. Complete the payment.

Expected:

- [ ] The browser returns to `/orders/<public_id>`.
- [ ] The order shows **Payment confirmed** only after the webhook, not merely
      because the browser callback fired.
- [ ] `payments.status = captured`, `orders.status = paid`,
      `orders.paid_at` is set, and `order_items.stock_state = sold`.
- [ ] A `payment.captured` (and/or `order.paid`) `webhook_events` row is
      `processed`.
- [ ] A confirmation email is queued and, if SMTP is configured, sent. Check
      Mailpit at `http://localhost:8025` or `make outbox`.
- [ ] `make reconcile` reports no mismatch for the order.

Record: public order id, Razorpay payment id, event ids, timestamp, result.

## 5. One failed payment

1. Create a new order the same way.
2. In Razorpay Checkout, use a failure test method (the dashboard documents the
   current failure card/UPI handle). Alternatively dismiss the checkout.
3. Do not pay.

Expected:

- [ ] The order does not become `paid`.
- [ ] A `payment.failed` webhook, if Razorpay sends one, is `processed` and the
      order becomes `payment_failed` (or stays `awaiting_payment` until expiry).
- [ ] Stock is released on expiry/failure, not sold.
- [ ] `make reconcile` reports no mismatch.

Record: public order id, payment id, event ids, result.

## 6. Replay a webhook

1. In the Razorpay dashboard, open the successful payment's
   `payment.captured` event.
2. Choose **Resend** / replay.
3. Watch the API log and `webhook_events`.

Expected:

- [ ] The replay is acknowledged as a duplicate.
- [ ] No second sale, no double stock decrement, no duplicate paid transition.
- [ ] The order stays `paid` with one captured payment.
- [ ] `make reconcile` still reports no mismatch.

Record: event id, replay timestamp, result.

Also replay a **failed** event after fixing its cause, and confirm the intake
reprocesses it (a `failed` row is allowed to be retried; a `processed` row is
not).

## 7. Test UPI pending → captured delay (if available)

If the test account exposes UPI, start a UPI payment and let it stay pending,
then approve it after a delay. Confirm:

- [ ] The order waits in `awaiting_payment`.
- [ ] The later capture webhook still marks it `paid` if stock is available.
- [ ] If the reservation expired first, the late-payment path re-reserves or
      refunds, never silently confirms.

## 8. Close out

- [ ] Remove the tunnel.
- [ ] Deactivate the test webhook or point it at a stable staging URL.
- [ ] Remove the test keys from the shell/environment if they were exported
      manually. They stay in the ignored `.env` only.
- [ ] Record every result above in the milestone evidence, with ids and
      timestamps.
- [ ] If anything failed, file the fix; do not mark the gate passed.

## What this drill does not prove

- Live-key behaviour, real settlement, refunds to real instruments.
- Razorpay uptime or latency under load.
- Webhook delivery under retries beyond what was observed.
- That the amount/currency review path is correct for a real mismatch; that is
  covered by tests, and a manual mismatch drill is still worth doing in staging.
