# Spec 03 — Domain Model

Modelagem tática DDD implementada em `backend/app/domain/`.

## Shared Kernel

| Tipo | Arquivo | Descrição |
|------|---------|-----------|
| VO | `shared/value_objects/money.py` | Valores monetários em centavos |
| VO | `shared/value_objects/email.py` | E-mail normalizado e validado |
| VO | `shared/value_objects/cep.py` | CEP brasileiro (8 dígitos) |
| VO | `shared/value_objects/phone.py` | Telefone internacional |
| VO | `shared/value_objects/address.py` | Endereço completo |
| VO | `shared/value_objects/sku.py` | SKU de produto |
| Base | `shared/aggregate_root.py` | Coleta de domain events |
| Base | `shared/domain_event.py` | Evento base |
| Base | `shared/exceptions.py` | `DomainError` |

## Agregados MVP

### User (Identity & Access)

- **Raiz:** `User`
- **Entidades:** `Role`, `UserAddress`
- **Invariantes:** nome ≥ 2 chars; MFA só com e-mail verificado; endereço default único
- **Eventos:** `UserRegistered`, `UserEmailVerified`, `UserPasswordChanged`, `UserDeactivated`
- **Repositório (Spec 05):** `UserRepository`

### Product (Catalog)

- **Raiz:** `Product`
- **Entidades:** `ProductVariation`, `ProductImage`
- **Invariantes:** publicar exige imagem, preço > 0 e descrição; SKU único por variação
- **Eventos:** `ProductCreated`, `ProductPublished`, `ProductPriceChanged`, `ProductDeactivated`
- **Repositório (Spec 05):** `ProductRepository`

### Cart (Order Management)

- **Raiz:** `Cart`
- **Entidades:** `CartItem`
- **Invariantes:** requer `customer_id` ou `session_id`; quantidade > 0
- **Eventos:** `CartItemAdded`, `CartCleared`
- **Repositório (Spec 05):** `CartRepository`

### Order (Order Management)

- **Raiz:** `Order`
- **Entidades:** `OrderItem`, `OrderStatusHistory`
- **Invariantes:** ≥ 1 item; desconto ≤ subtotal; transições de status controladas
- **Eventos:** `OrderCreated`, `OrderPaid`, `OrderCancelled`, `OrderStatusChanged`
- **Repositório (Spec 05):** `OrderRepository`

## Regras

- Zero imports de FastAPI, SQLAlchemy ou Redis no domínio
- Referências cross-aggregate por `EntityId`, nunca por objeto
- Factory `create()` emite eventos; `reconstitute()` não emite

## Próximo passo

→ Spec 04: use cases (`RegisterUser`, `LoginUser`, `CreateProduct`, `AddToCart`, `Checkout`)
