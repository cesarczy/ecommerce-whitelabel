# E-commerce Whitelabel

Plataforma e-commerce modular com identidade configurável (whitelabel), construída com **Clean Architecture**, **DDD** e pipeline de 12 specs.

## Stack

| Camada | Tecnologias |
|--------|-------------|
| Backend | FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, Redis, JWT (Argon2) |
| Frontend | Angular 20, Angular Material, NGXS, TailwindCSS |
| Infra | Docker Compose (PostgreSQL, Redis, RabbitMQ, MinIO) |

## Quick start

```bash
# 1. Infraestrutura
docker compose -f docker/docker-compose.yml up -d

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload

# 3. Frontend (Node.js 20+)
cd frontend
npm install
npm start
```

- API: http://localhost:8000/docs  
- App: http://localhost:4200

## Estrutura

```
ecommerce-whitelabel/
├── backend/          # FastAPI — Clean Architecture
├── frontend/         # Angular 20 SPA
├── docker/           # Compose dev
├── docs/             # Discovery, context map, harness report
├── specs/            # 12 specs DDD
└── harness/          # Validação arquitetural
```

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [Discovery](docs/discovery.md) | Requisitos, MVP, stack |
| [Glossário](docs/glossary.md) | Linguagem ubíqua |
| [Context Map](docs/context-map.md) | Bounded contexts |
| [Domain Model](docs/domain-model.md) | Agregados |
| [Ports & Adapters](docs/ports-adapters.md) | Interfaces e adapters |
| [Database Schema](docs/database-schema.md) | SQLAlchemy + Alembic |
| [DI Plan](docs/di-plan.md) | Wiring FastAPI |
| [Harness Report](docs/harness-report.md) | Validação final |

## Pipeline de specs

| Spec | Status |
|------|--------|
| 01–12 | ✅ Concluídas |

Validação: `./harness/scripts/run-harness.sh`

## Arquitetura backend

```
backend/app/
├── core/           # Config, security, database
├── domain/         # Entidades, VOs, agregados
├── application/    # Use cases, DTOs, ports
├── infra/          # Repositories, mappers, ORM
└── api/            # Routers REST v1
```

## Testes

```bash
cd backend && pytest tests/ --cov=app
```

## Licença

Projeto privado.
