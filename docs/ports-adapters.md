# Ports & Adapters — Spec 05

Interfaces em `backend/app/application/interfaces/ports.py`.

## Repository ports

| Port | Aggregate | Adapter |
|------|-----------|---------|
| `UserRepository` | User | `SqlAlchemyUserRepository` |
| `ProductRepository` | Product | `SqlAlchemyProductRepository` |
| `CartRepository` | Cart | `SqlAlchemyCartRepository` |
| `OrderRepository` | Order | `SqlAlchemyOrderRepository` |

## Service ports

| Port | Adapter |
|------|---------|
| `PasswordHasher` | `Argon2PasswordHasher` |
| `TokenService` | `JWTTokenService` |
| `RefreshTokenStore` | `SqlAlchemyRefreshTokenStore` |
| `EventBus` | `InMemoryEventBus` (RabbitMQ em Fase 2) |
| `UnitOfWork` | `SqlAlchemyUnitOfWork` |

## Adapters planejados (Fase 2)

- `MercadoPagoPaymentAdapter`
- `MinIOStorageAdapter`
- `SmtpEmailAdapter`
- `RedisCacheAdapter`
- `RabbitMQEventBus`

## DI

Ver `docs/di-plan.md` e `backend/app/api/deps.py`.
