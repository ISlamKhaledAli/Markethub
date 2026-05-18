# Markethub — Payments & promotions (backend)

This project uses **Django REST Framework** with a pluggable payment provider (`mock` now, `stripe` later). Promotions discount cart totals at checkout; totals are always recomputed on the server.

## Environment variables

Add to your `.env` (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `PAYMENT_PROVIDER` | `mock` or `stripe` (Stripe not implemented yet) | `mock` |
| `PAYMENT_WEBHOOK_SECRET` | Shared secret for `POST /api/payments/simulate-webhook/` (and future real webhooks) | `dev-webhook-secret-change-me` |

Existing variables (`SECRET_KEY`, `DATABASE_URL`, `FRONTEND_URL`, email, Redis, etc.) are unchanged.

## Payment flow (mock)

1. **Checkout** creates one `Order` per seller (`pending`).
2. **Create intent** — `POST /api/payments/create-intent/` with `{ "order_id": <id> }`.  
   Amount is **always** taken from `Order.total_amount` (never from the client).  
   Response includes `client_secret` and `transaction_id` (mock-shaped, Stripe-ready field names).
3. **Confirm** — `POST /api/payments/verify/` with `payment_id`, `client_secret`, and optional `simulate_outcome`:  
   `succeeded` | `failed` | `processing` | `pending` | `random`.
4. **Success** → `Payment.status = succeeded`, `Order.status = accepted`.  
   **Failed** → payment failed, order stays `pending`.
5. **Webhook simulation** — `POST /api/payments/simulate-webhook/` with header  
   `X-Payment-Webhook-Secret: <PAYMENT_WEBHOOK_SECRET>` and JSON  
   `{ "transaction_id": "<txn>", "event": "succeeded" | "failed" | "refunded" }`.

Zero-total orders get an immediate **succeeded** payment record (no provider call).

## Payment history visibility (`GET /api/payments/history/`)

- **Customers**: payments where they are the payer (`Payment.user`).
- **Sellers**: payments tied to orders for their `SellerProfile`.
- **Admins**: all payments.

Each row includes `buyer_email` and `seller_name` (from the related order) for admin/seller dashboards.

## Promo flow

- **Validate** — `POST /api/promos/validate/` `{ "code": "SAVE10" }` (auth required, uses current cart).
- **Apply** — `POST /api/promos/apply/` same body; stores promo on the cart.
- **Checkout** applies the discount server-side (proportional split across seller subtotals) and increments `used_count` once per checkout.
- **Admin CRUD** — `GET/POST /api/promos/`, `GET/PATCH/DELETE /api/promos/<id>/` (admin role only).

## API summary (envelope)

Successful responses match existing auth style:

```json
{
  "status": "success",
  "message": "...",
  "data": { }
}
```

Errors:

```json
{
  "status": "error",
  "message": "...",
  "data": { }
}
```

Order/cart endpoints under `/api/orders/` remain **raw DRF JSON** (unchanged).

## Switching to Stripe later

1. Implement `StripePaymentProvider` in `payments/providers/stripe.py` using the same `BasePaymentProvider` methods.
2. Point `PAYMENT_PROVIDER=stripe` and add Stripe keys to `.env`.
3. Keep **`Payment`**, URLs, and request bodies stable so the frontend does not need breaking changes.

## Tests

```bash
.venv/bin/python manage.py test payments promos
```

## Suggested Git workflow

- Branch: `feature/payments-and-promos`
- PR title: **feat(backend): mock payments, webhooks, and promo codes**
- PR body: describe provider abstraction, checkout integration, env vars, and manual test steps (create order → intent → verify → history).
