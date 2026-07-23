# Discovery — E-commerce Whitelabel

## 1. Visão do produto

Plataforma **e-commerce whitelabel** modular, pronta para múltiplas lojas com identidade visual e configurações próprias, compartilhando o mesmo núcleo de negócio. Objetivo: entregar experiência comparável a soluções comerciais (VTEX, Shopify-like) com controle total do código, arquitetura limpa e extensibilidade para integrações de pagamento, frete e marketing.

### Problema de negócio

Empresas e agências precisam lançar lojas virtuais rapidamente, com catálogo, checkout, pagamentos e painel administrativo, sem reconstruir do zero a cada cliente. Soluções SaaS fechadas limitam customização; builds ad hoc geram dívida técnica. Este produto oferece **base reutilizável + whitelabel** com arquitetura sustentável.

### Proposta de valor

| Para quem | Valor |
|-----------|-------|
| Agência / integrador | Deploy de loja nova em dias, não meses |
| Lojista | Catálogo, carrinho, checkout, relatórios |
| Operador admin | Gestão de produtos, pedidos, estoque, cupons |
| Desenvolvedor | API REST documentada, DDD, testes, Docker |

---

## 2. Personas

### Cliente final (Shopper)
- Navega catálogo, adiciona ao carrinho, aplica cupom, finaliza compra
- Gerencia perfil, endereços, favoritos, histórico e avaliações
- Pode usar login social (Google, GitHub) e MFA

### Administrador da loja (Store Admin)
- Configura whitelabel (tema, banners, SEO)
- Gerencia produtos, categorias, marcas, estoque, cupons
- Acompanha dashboard (vendas, conversão, estoque baixo)
- Gerencia usuários internos e permissões (RBAC)

### Funcionário / Operador
- Atualiza pedidos, estoque, atendimento
- Permissões restritas por papel

### Super Admin (plataforma — fase futura)
- Gerencia múltiplas lojas (tenants)
- Fora do MVP inicial; arquitetura preparada via `tenant_id`

---

## 3. Jornadas principais

### J1 — Compra (happy path)
1. Cliente acessa home whitelabel
2. Busca/navega produtos por categoria
3. Adiciona itens ao carrinho (sessão ou autenticado)
4. Aplica cupom / visualiza frete (ViaCEP + Correios)
5. Checkout → escolhe pagamento (PIX, boleto, cartão)
6. Gateway processa → pedido confirmado → notificação e-mail
7. Cliente acompanha status no histórico

### J2 — Onboarding de loja (whitelabel)
1. Admin configura identidade (logo, cores, domínio)
2. Importa ou cadastra catálogo
3. Configura métodos de pagamento e frete
4. Publica loja

### J3 — Gestão operacional
1. Admin visualiza dashboard
2. Identifica produtos com estoque baixo
3. Atualiza inventário, processa pedidos pendentes
4. Consulta relatórios financeiros e auditoria

---

## 4. Requisitos funcionais (MoSCoW)

### Must (MVP — Fase 1)

**Identidade & Acesso**
- Cadastro, login, refresh token, logout
- Perfil e endereços
- RBAC básico (admin, customer, staff)
- Hash Argon2, JWT

**Catálogo**
- Produtos, categorias, subcategorias, marcas
- SKU, preço, imagens (MinIO)
- Busca e listagem paginada

**Carrinho & Pedidos**
- Carrinho persistente (Redis + DB)
- Checkout com endereço e frete estimado
- Pedido com status (criado → pago → enviado → entregue)
- Itens de pedido

**Pagamentos (abstração)**
- Interface de gateway plugável
- Implementação inicial: mock ou Mercado Pago sandbox
- PIX e cartão na interface

**Admin**
- Dashboard básico (vendas, pedidos, estoque baixo)
- CRUD produtos, categorias, pedidos
- Gestão de usuários clientes

**Infra**
- Docker Compose (dev): API, PostgreSQL, Redis, RabbitMQ, MinIO
- OpenAPI / Swagger

### Should (Fase 2)

- Cupons e cashback
- Avaliações de produtos
- Favoritos
- Esqueci senha / confirmar e-mail
- OAuth2 (Google, GitHub)
- MFA
- Notificações (e-mail via Celery + RabbitMQ)
- Relatórios avançados
- SEO por produto/categoria
- Produtos relacionados / recomendados
- Stripe, PagSeguro, Asaas
- Boleto
- Nota fiscal (interface preparada)

### Could (Fase 3)

- Multi-tenant completo (várias lojas isoladas)
- Marketing (banners, campanhas)
- Vídeos em galeria
- Cloudflare R2 como storage alternativo
- CQRS em relatórios e dashboard
- Conversão e analytics avançados

### Won't (agora)

- App mobile nativo
- Marketplace multi-vendedor
- ERP completo integrado

---

## 5. Requisitos não-funcionais

| Área | Requisito |
|------|-----------|
| Performance | API p95 < 300ms em endpoints de leitura (catálogo) |
| Segurança | JWT + refresh rotation, RBAC, rate limit, CORS, CSRF, Argon2 |
| Escalabilidade | Stateless API; filas para tarefas assíncronas |
| Disponibilidade | Health checks; retry em integrações externas |
| Observabilidade | Logs estruturados, auditoria de ações admin |
| Testabilidade | Pytest + coverage ≥ 70% no backend (meta Fase 2) |
| Documentação | OpenAPI auto-gerado; ReDoc |
| i18n | PT-BR inicial; strings externalizáveis no frontend |

---

## 6. Stack técnica

### Backend
- **FastAPI** — API REST, DI nativa, OpenAPI
- **SQLAlchemy 2.0** + **Alembic** — ORM e migrations
- **PostgreSQL** — persistência principal
- **Redis** — cache, sessão de carrinho, rate limit
- **RabbitMQ** + **Celery** — filas e tarefas assíncronas
- **MinIO** — object storage (imagens, assets whitelabel)
- **Pydantic v2** — validação e DTOs

### Frontend
- **Angular 20** — SPA
- **Angular Material** + **TailwindCSS**
- **NGXS** — state management (preferência sobre NGRX por simplicidade)
- **RxJS** + **Signals**

### DevOps
- **Docker** + **Docker Compose** (dev e prod)
- **Nginx** — reverse proxy em produção

### Integrações (interfaces preparadas)
- Pagamentos: Mercado Pago, Stripe, PagSeguro, Asaas
- Frete: ViaCEP, Correios
- Storage: MinIO, Cloudflare R2
- Auth social: Google, GitHub
- E-mail: SMTP

---

## 7. Arquitetura

- **Clean Architecture** — dependências apontam para dentro
- **DDD** — bounded contexts, agregados, linguagem ubíqua
- **Repository Pattern** + **Unit of Work**
- **CQRS** — em dashboard, relatórios e consultas pesadas
- **SOLID** + **Dependency Injection** (FastAPI Depends + containers)

### Estrutura monorepo

```
ecommerce-whitelabel/
├── backend/          # FastAPI
├── frontend/         # Angular 20
├── docker/           # Compose, Nginx, configs
├── docs/             # Discovery, context map, ADRs
├── specs/            # Pipeline de specs (kit DDD)
└── harness/          # Validação arquitetural (adaptado)
```

### Camadas backend

```
backend/app/
├── core/           # Config, security, exceptions, middlewares
├── domain/         # Entidades, VOs, agregados, eventos (sem framework)
├── application/    # Commands, queries, DTOs, interfaces (portas)
├── infra/          # Repositories, providers, storage, email
└── api/            # Routers FastAPI (v1)
```

---

## 8. Modelo de dados (visão)

Mais de 40 entidades agrupadas por contexto. Principais agregados:

| Agregado | Entidades relacionadas |
|----------|------------------------|
| User | users, roles, permissions, addresses |
| Product | products, product_images, product_variations, brands, tags |
| Category | categories (tree) |
| Cart | cart, cart_items |
| Order | orders, order_items, order_status_history |
| Payment | payments, payment_methods |
| Coupon | coupons, coupon_usages |
| Inventory | inventory, stock_movements |
| Review | reviews |
| Notification | notifications |
| Audit | logs, audit_trail |
| Store (whitelabel) | store_settings, themes, banners, seo_metadata |

---

## 9. Escopo MVP (Fase 1 — entrega incremental)

**Objetivo:** loja funcional single-tenant com admin, catálogo, carrinho, checkout e pagamento simulado.

| Sprint | Entrega |
|--------|---------|
| S0 | Discovery, context map, estrutura monorepo, Docker base |
| S1 | Auth (JWT + refresh), users, RBAC, perfil |
| S2 | Catálogo (produtos, categorias, marcas, imagens MinIO) |
| S3 | Carrinho (Redis) + checkout + pedidos |
| S4 | Pagamento (porta + adapter mock/MP sandbox) |
| S5 | Admin dashboard + CRUDs essenciais |
| S6 | Frontend: login, catálogo, carrinho, checkout, admin básico |
| S7 | Testes, documentação, hardening segurança |

---

## 10. Premissas

- Uma loja por deploy no MVP (whitelabel via config, não multi-tenant ainda)
- PostgreSQL como única fonte de verdade transacional
- Imagens servidas via MinIO (presigned URLs)
- Frontend consome API REST versionada (`/api/v1`)
- Pagamento inicial via adapter único; demais gateways em Fase 2

---

## 11. Riscos

| Risco | Mitigação |
|-------|-----------|
| Escopo grande demais | MVP rígido; MoSCoW; entregas por sprint |
| Complexidade de pagamentos | Porta abstrata + adapter por gateway |
| Divergência frontend/backend | OpenAPI como contrato; DTOs espelhados |
| Performance de catálogo | Cache Redis; índices DB; paginação |
| Segurança | RBAC, rate limit, auditoria desde Fase 1 |

---

## 12. Adaptação do kit DDD

O kit original assume TypeScript + Prisma. Este projeto adapta:

| Kit original | Este projeto |
|--------------|--------------|
| Prisma | SQLAlchemy 2.0 + Alembic |
| Express/Fastify | FastAPI |
| React | Angular 20 |
| `src/modules/` | `backend/app/domain/<context>/` |
| Spec 07 prisma-schema | Spec 07 → SQLAlchemy models + Alembic |

Regras de dependência e DDD permanecem iguais: **domínio no centro, sem imports de framework**.
