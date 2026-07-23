# Module Structure — Spec 06

## Monorepo

```
ecommerce-whitelabel/
├── backend/app/
│   ├── core/           # Config, DB, security, middlewares
│   ├── domain/         # Bounded contexts (sem framework)
│   ├── application/    # Use cases, DTOs, ports
│   ├── infra/          # ORM, repositories, adapters
│   └── api/            # FastAPI routers
├── frontend/src/app/
│   ├── core/
│   ├── shared/
│   ├── layout/
│   ├── pages/
│   └── admin/
├── docker/
├── docs/
└── specs/
```

## Bounded contexts (domain/)

| Pasta | Contexto |
|-------|----------|
| users/ | Identity & Access |
| products/, categories/ | Catalog |
| orders/ | Cart + Order |
| payments/ | Payment (Fase 2) |
| shared/ | Shared Kernel |

## Regra de dependência

```
api → application → domain
infra → application → domain
```

Domínio no centro — nunca importa `infra`, `api`, FastAPI ou SQLAlchemy.
