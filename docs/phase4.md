# Phase 4 — E-commerce Whitelabel

Backlog **Should/Could** do discovery.md — growth, marketing e auth completo.

## Entregue

| Módulo | Status |
|--------|--------|
| Favoritos | Add/remove/list por usuário |
| SEO produto | PUT `/products/{id}/seo`, slug route |
| Produtos relacionados | Mesma categoria, até 6 itens |
| Esqueci senha | Token + e-mail via Celery (fallback log) |
| Confirmar e-mail | Token no registro + verify/resend |
| Banner CRUD | Admin create/delete + presigned URLs na home |
| Vídeos em galeria | POST/GET `/products/{id}/videos` |
| Analytics avançado | Conversão real (pedidos/carrinhos), favoritos, reviews |
| Cloudflare R2 | Adapter S3-compatible + `STORAGE_PROVIDER=r2` |

## Novos endpoints

```
POST   /api/v1/favorites/{product_id}
DELETE /api/v1/favorites/{product_id}
GET    /api/v1/favorites
GET    /api/v1/products/slug/{slug}
GET    /api/v1/products/{id}/related
PUT    /api/v1/products/{id}/seo
POST   /api/v1/admin/banners
DELETE /api/v1/admin/banners/{id}
GET    /api/v1/store/banners/presigned
POST   /api/v1/products/{id}/videos
GET    /api/v1/products/{id}/videos
POST   /api/v1/auth/forgot-password
POST   /api/v1/auth/reset-password
POST   /api/v1/auth/verify-email
POST   /api/v1/auth/resend-verification
GET    /api/v1/admin/analytics
```

## Storage (MinIO ou R2)

```env
STORAGE_PROVIDER=minio   # ou r2
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET=ecommerce
R2_ENDPOINT=
```

## Frontend

- Detalhe do produto com relacionados e favorito
- Página de favoritos
- Esqueci senha / reset / verify e-mail
- Home com carrossel de banners
- Admin: banners + analytics no dashboard

## Testes

39 testes passando + harness PASS.
