# Database Schema — Spec 07 (SQLAlchemy + Alembic)

Adaptação da spec Prisma para **SQLAlchemy 2.0** + **Alembic**.

## Entidades MVP

| Tabela | Contexto |
|--------|----------|
| users, roles, user_roles, user_addresses | Identity |
| categories | Catalog |
| products, product_images, product_variations | Catalog |
| carts, cart_items | Order |
| orders, order_items, order_status_history | Order |
| refresh_tokens | Identity |

## Migrations

```bash
cd backend
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

Dev: `create_all` no lifespan da app (`app/main.py`).

## Mappers

`backend/app/infra/mappers/mappers.py` — conversão domain ↔ ORM.

Regra: domínio **nunca** importa SQLAlchemy.
