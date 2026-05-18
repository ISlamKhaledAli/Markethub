# Stripe integration

## Environment

Set in `.env` (never commit real keys):

```env
PAYMENT_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=http://localhost:4200
```

Keep `PAYMENT_PROVIDER=mock` for offline development without Stripe.

## Flow

1. Checkout creates pending order(s).
2. `POST /api/payments/create-intent/` creates a Stripe Checkout Session.
3. Response includes `checkout_url` — frontend redirects the browser there.
4. On success, Stripe redirects to `{FRONTEND_URL}/payment/success?payment_id=…&session_id=…`.
5. Frontend calls `POST /api/payments/verify/` with `session_id`.
6. Stripe webhooks (`POST /api/payments/stripe-webhook/`) also confirm payment and run fulfillment.

Inventory and promo usage run only after **succeeded** payment (unchanged).

## Webhook (local)

```bash
stripe listen --forward-to localhost:8000/api/payments/stripe-webhook/
```

Copy the `whsec_…` signing secret into `STRIPE_WEBHOOK_SECRET`.

## Test cards

| Scenario | Number |
|----------|--------|
| Success | `4242 4242 4242 4242` |
| Decline | `4000 0000 0000 0002` |
| 3D Secure | `4000 0025 0000 3155` |

Use any future expiry, any CVC, any billing ZIP.
