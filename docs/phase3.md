# Phase 3 — E-commerce Whitelabel

## Entregue

| Módulo | Status |
|--------|--------|
| Payment webhooks | MP/Stripe/Mock via `POST /webhooks/payments/{provider}` |
| Reviews | Agregado, repo, API de criação e listagem |
| Store settings | Branding por tenant (nome, cores, logo) |
| Banners | Query de banners ativos por tenant |
| Histórico de pedidos | `GET /orders` para cliente autenticado |
| Notificações e-mail | Celery dispara e-mail em eventos de pedido/pagamento |
| Tenant isolation | Filtro `tenant_id` em reviews, store e banners |

## Novos endpoints

```
POST /api/v1/webhooks/payments/{provider}
GET  /api/v1/orders
POST /api/v1/reviews
GET  /api/v1/products/{id}/reviews
GET  /api/v1/products/{id}/rating
GET  /api/v1/store/settings
PUT  /api/v1/store/settings
GET  /api/v1/store/banners
```

## Webhook (exemplo)

```json
POST /api/v1/webhooks/payments/mock
{
  "external_id": "pay_abc123",
  "status": "approved"
}
```

## Frontend (Angular)

- Checkout com cupom e pagamento mock
- Página de pedidos do cliente
- MFA enroll/verify
- Admin: cupons e configurações da loja

## Celery + e-mail

Com `USE_CELERY_EVENTS=true`, eventos `OrderCreatedEvent`, `PaymentConfirmedEvent` e `OrderPaidEvent` enfileiram `send_email_task`.

```bash
cd backend
celery -A app.infra.workers.celery_app worker --loglevel=info
```

## Header multi-tenant

```
X-Tenant-Slug: default
```
