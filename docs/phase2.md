# Phase 2 — E-commerce Whitelabel

## Entregue

| Módulo | Status |
|--------|--------|
| Multi-tenant | Middleware `X-Tenant-Slug`, seed tenant `default` |
| Inventory | Agregado, repo, reserva no checkout |
| Coupons | Agregado, repo, desconto no checkout |
| Payments | Agregado, Mercado Pago/Stripe/Mock adapters |
| MinIO | Upload + presigned URL |
| MFA | TOTP enroll/verify |
| OAuth2 | Google + GitHub authorize/callback |
| Celery/RabbitMQ | Tasks + CeleryEventBus (opt-in) |
| CQRS Dashboard | Query real via SQLAlchemy |

## Novos endpoints

```
POST /api/v1/coupons
PUT  /api/v1/inventory
POST /api/v1/payments
POST /api/v1/products/{id}/upload
POST /api/v1/auth/mfa/enroll
POST /api/v1/auth/mfa/verify
GET  /api/v1/auth/oauth/{provider}/authorize
GET  /api/v1/auth/oauth/callback
GET  /api/v1/admin/dashboard  (CQRS)
```

## Config (.env)

```
USE_CELERY_EVENTS=true
CELERY_BROKER_URL=amqp://ecommerce:ecommerce@localhost:5672//
MERCADO_PAGO_ACCESS_TOKEN=
STRIPE_SECRET_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
OAUTH_REDIRECT_URI=http://localhost:8000/api/v1/auth/oauth/callback
```

## Celery worker

```bash
cd backend
celery -A app.infra.workers.celery_app worker --loglevel=info
```

## Header multi-tenant

```
X-Tenant-Slug: default
```
