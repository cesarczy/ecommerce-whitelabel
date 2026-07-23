# Backend — E-commerce Whitelabel

API FastAPI com Clean Architecture e DDD.

## Camadas

| Camada | Pasta | Responsabilidade |
|--------|-------|------------------|
| Core | `app/core/` | Config, security, DB session, exceptions |
| Domain | `app/domain/` | Entidades, VOs, agregados, eventos |
| Application | `app/application/` | Commands, queries, DTOs, portas |
| Infra | `app/infra/` | Repositories, adapters, storage |
| API | `app/api/` | Routers FastAPI |

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## Regras

- Domínio **nunca** importa FastAPI, SQLAlchemy ou Redis
- Use cases orquestram; controllers só traduzem HTTP ↔ DTO
- Repositórios persistem agregados inteiros
