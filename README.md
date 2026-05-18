# Markethub

Full-stack e-commerce marketplace: **Angular** + **Django REST Framework** + **MySQL**, with JWT auth, cart/checkout, mock payments, promo codes, and role-based admin/seller dashboards.

## Stack

| Layer | Technology |
|-------|------------|
| API | Django 5, DRF, SimpleJWT |
| DB | MySQL (or SQLite for local dev via `DATABASE_URL`) |
| UI | Angular 21, Angular Material, Tailwind |
| Async | Celery + Redis (optional) |

## Local setup

### Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit SECRET_KEY, DATABASE_URL, email settings
python manage.py migrate
python manage.py seed_data          # realistic QA catalog, orders, payments
python manage.py runserver
```

Re-run from scratch: `python manage.py seed_data --flush`

Useful `.env` keys (see `.env.example`):

- `DEBUG=True` — development mode
- `REGISTER_AUTO_VERIFY=True` — skip email verification locally
- `PAYMENT_PROVIDER=mock` — simulated payments
- `ALLOWED_HOSTS=localhost,127.0.0.1`

### Frontend

```bash
cd frontend
npm install
npm start                 # dev server → http://localhost:4200
npm run build             # production build (uses environment.production.ts)
```

Development API URL: `http://localhost:8000/api` (`environment.development.ts`).  
Production build uses relative `/api` (configure reverse proxy to Django).

## API overview

| Prefix | Domain |
|--------|--------|
| `/api/auth/` | Register, login, JWT refresh, profile |
| `/api/products/` | Catalog, categories, seller products |
| `/api/orders/` | Cart, checkout, buyer/seller orders |
| `/api/payments/` | Payment intents, verify, history |
| `/api/promos/` | Validate, apply, admin CRUD |

Envelope responses (`status`, `message`, `data`) are used for auth, payments, and promos. Cart/orders return raw DRF payloads.

Payment & promo details: [docs/PAYMENTS_AND_PROMOS.md](docs/PAYMENTS_AND_PROMOS.md)

## Seed / QA accounts

After `python manage.py seed_data`:

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@example.com` | `Admin123!` |
| Seller | `seller1@example.com` / `seller2@example.com` | `Seller123!` |
| Customer | `customer@example.com` | `Customer123!` |

Also seeds: 7 top-level categories + subcategories, 44 products (with 2 images each), promo codes (`SUMMER20`, `EXPIRED99`, …), orders/payments in multiple states, reviews, and wishlist rows.

## Roles

- **customer** — browse, cart, checkout, pay
- **seller** — manage products, view orders/revenue (`/seller`)
- **admin** — users, promos, payments, all orders (`/admin`)

Admin accounts cannot be created via public registration.

## Production checklist

### Backend

- Set `DEBUG=False`, strong `SECRET_KEY`, explicit `ALLOWED_HOSTS`
- Use MySQL `DATABASE_URL`; run `python manage.py migrate`
- Set `REGISTER_AUTO_VERIFY=False` and configure SMTP
- Set `PAYMENT_PROVIDER=mock` only in staging; use real provider in production
- Set strong `PAYMENT_WEBHOOK_SECRET`; disable `ENABLE_PAYMENT_WEBHOOK_SIMULATION`
- Serve static/media via nginx or whitenoise + object storage
- Put TLS in front; review `SECURE_*` settings in `config/settings.py`

### Frontend

- `npm run build` — validates production bundle
- Configure reverse proxy: `/api` → Django, `/` → `frontend/dist`
- Set `FRONTEND_URL` in Django for CORS

### Tests

```bash
source .venv/bin/activate
python manage.py test
cd frontend && npm run build
```

## Order & payment flow

1. Checkout creates **pending** orders (stock is validated, not decremented).
2. Payment intent → verify (or webhook) on success.
3. Inventory and promo usage are applied **only after successful payment**.

This prevents lost stock when payments fail or are abandoned.
