# DI Plan — Spec 10

## FastAPI Depends (`backend/app/api/deps.py`)

| Dependency | Provides |
|------------|----------|
| `get_session` | `AsyncSession` |
| `get_uow` | `SqlAlchemyUnitOfWork` |
| `get_register_user` | `RegisterUserUseCase` |
| `get_login_user` | `LoginUserUseCase` |
| `get_current_user_id` | `UUID` from JWT |

## Lifespan (`app/main.py`)

1. `create_all` tables
2. `seed_default_roles`
3. Graceful `engine.dispose()` on shutdown

## Event flow

1. Use case mutates aggregate
2. `uow.commit()`
3. `event_bus.publish(collected_events)`

## Cross-context (MVP)

In-process logging via `InMemoryEventBus`. RabbitMQ handlers em Fase 2.
