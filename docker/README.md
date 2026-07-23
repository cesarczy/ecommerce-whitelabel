# Docker — E-commerce Whitelabel

## Desenvolvimento

```bash
docker compose -f docker/docker-compose.yml up -d
```

## Serviços

| Serviço | Porta | Credenciais |
|---------|-------|-------------|
| PostgreSQL | 5432 | `ecommerce` / `ecommerce` |
| Redis | 6379 | — |
| RabbitMQ | 5672, 15672 (UI) | `ecommerce` / `ecommerce` |
| MinIO | 9000, 9001 (console) | `minioadmin` / `minioadmin` |

## Parar

```bash
docker compose -f docker/docker-compose.yml down
```
