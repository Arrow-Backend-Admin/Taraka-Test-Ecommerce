# Known limitations

This file is deliberately uncomfortable reading. It lists what the current
Milestone 1–3 hardening does **not** prove, and where a human or an external
party still has to act. Nothing here is a promise that the system is foolproof.

Last updated: 4 November 2026. Scope: Phase 4 Milestones 1–3 plus the hardening
gate. Shipments, returns/exchanges, coupons and authentication are not started.

## Verification gaps

| Area | Status | Detail |
|---|---|---|
| PostgreSQL test suite | UNVERIFIED locally | The suite has only been run on SQLite on this machine. CI runs it against PostgreSQL 16. |
| Mailpit delivery | UNVERIFIED locally | `tests/test_mail_mailpit.py` skips without `MAILPIT_URL`. CI starts Mailpit and runs it. The refused-SMTP payment test does run locally. |
| Alembic upgrade/downgrade on PostgreSQL | UNVERIFIED locally | CI runs `upgrade head → downgrade -1 → upgrade head → alembic check` against PostgreSQL. |
| Backup/restore on PostgreSQL | UNVERIFIED locally | Only the SQLite round-trip ran locally. The PostgreSQL scratch-database restore runs in CI when `pg_dump`/`pg_restore` exist. |
| Playwright E2E, axe and Lighthouse | UNVERIFIED locally | Browsers and Lighthouse were not installed locally. CI installs Chromium and runs the mobile suite. |
| Schemathesis fuzzing | UNVERIFIED locally | Schemathesis is not installed in the local virtualenv; CI runs it against every documented endpoint. |
| pip-audit | UNVERIFIED locally | `pip-audit` is not installed locally; CI installs and runs it. |
| Real Razorpay test-mode payment | UNVERIFIED | No real test-mode transaction, webhook delivery or replay has been performed. See `brand/phase-4/razorpay-test-runbook.md`. |
| Human visual QA | OPEN | The retained placeholder photographs still need a human visual check. The launch guard blocks production use regardless. |

## Product and business facts still missing

These block publishing, not code:

- Seller legal name, state of registration and GSTIN.
- HSN code per product and the GST threshold basis (₹2,500) confirmation by a CA.
- Whether discounts are applied before or after GST extraction.
- Launch stock quantities per variant.
- Reverse-logistics cost per exchange from the 3PL.
- Exchange/return operational details, including who pays return shipping.
- COD decision (currently deferred; see `brand/phase-4/cod-decision-note.md`).

Until these are supplied, every product stays `draft`, and `make preflight` will
fail on the seller state/GSTIN checks.

## Security limitations

- **Authentication is not implemented.** Admin routes use a static bearer token.
  The token is refused when `APP_ENV=production` (the app refuses to start), and
  `make preflight` fails if it is set. This is a stop-gap, not an auth system.
- **Storefront CSP uses `'unsafe-inline'` for scripts.** Nonce-based CSP via a
  Next.js proxy is not implemented. This weakens XSS protection on the
  storefront. The API itself has a strict `default-src 'none'` policy.
- **Order access is capability-based.** The public order id is an unguessable
  token (144 bits). There is no logged-in customer identity, so "one customer
  cannot read another's order" is enforced by id entropy, not by authentication.
  Contact details are masked on public reads.
- **Rate limiting is per-IP for cart reservations only.** There is no general
  API rate limiter or WAF. A determined attacker can still generate load.
- **Secrets live in environment variables.** No secret manager or key rotation
  process exists yet.
- **Logs are redacted by pattern, not by schema.** Redaction covers tokens,
  authorization headers, email and phone shapes, but a novel secret format could
  slip through.

## Money and stock limitations

- **GST is extracted from GST-inclusive MRP per line.** The rate comes from the
  product snapshot, else 5% at or below ₹2,500 and 18% above. Discounts are not
  applied. A CA has not confirmed this treatment.
- **Shipping is ₹0 in this milestone.** No shipping calculator or address
  serviceability check exists.
- **Refunds are best-effort.** A failed refund call leaves the order in
  `refund_pending` with a note. There is no automatic retry worker for refunds.
- **Currency and amount mismatches are flagged, not auto-resolved.** A payment
  whose captured amount or currency differs from the order is marked
  `needs_review` and routed to refund; a human must reconcile it.
- **Reconciliation is read-only.** `make reconcile` reports mismatches and exits
  non-zero. It does not repair data.
- **Reservation expiry is a scheduled job.** If the sweeper is not scheduled,
  stock stays reserved until the next run. The API also expires lazily on read,
  but a stopped scheduler still delays release.
- **No inventory reservations across channels.** There is one stock pool. A
  future marketplace or retail channel is not modelled.

## Failure-mode limitations

- **Outbound calls have timeouts, bounded retries and a simple in-process
  circuit breaker.** The breaker is per process, so it resets on restart and is
  not shared across workers.
- **Email delivery is at-least-once.** The outbox can send a duplicate if a send
  succeeds but the status commit fails. Idempotency keys are not sent to the
  SMTP server (SMTP has no such concept).
- **Webhook intake is durable before acknowledgement.** A crash between storing
  the event and processing it leaves a `received` row. A replay inside the
  5-minute lease is treated as an in-flight duplicate; a replay after the lease
  is reclaimed and processed. An operator should still inspect rows that stay
  `received` longer than the lease; see `docs/runbooks/failing-webhooks.md`.
- **Graceful shutdown is bounded.** In-flight requests get a short grace period;
  a hard kill can still interrupt work. The outbox and webhook event row make
  the important state recoverable.
- **No chaos testing in production.** Crash-mid-transaction and dependency-down
  behaviour is covered by tests, not by a staging game day.

## Frontend limitations

- **Offline behaviour is a notice plus retry, not full offline support.** There
  is no service worker, offline cart or background sync.
- **Stock polling retries with backoff, then stops.** A long outage requires a
  page reload.
- **No internationalisation.** Copy is English with Indian English conventions.
- **No real device lab.** Playwright uses a Pixel 7 emulation profile and
  Chromium network throttling, not physical low-end Android hardware.

## Operational limitations

- **Single-region, single-database deployment.** No read replicas, failover or
  multi-region plan.
- **No alerting stack is configured.** Health endpoints exist; wiring them to
  paging is an operations task.
- **Backups are scripts, not a managed service.** Retention, encryption at rest
  and off-site storage are not automated here.
- **No load test has been run.** Capacity is unknown.
- **No penetration test or security review by an external party.**

## Explicit non-goals for this gate

Shipments, returns/exchanges, coupons, customer accounts, authentication, COD,
multi-currency and marketplace integrations. Do not describe the system as
production-ready until the UNVERIFIED rows above have evidence.
