# Glossário — E-commerce Whitelabel

Linguagem ubíqua do domínio. Termos usados de forma consistente em código, docs e conversas de negócio.

---

## A

### Agregado (Aggregate)
Cluster de entidades e value objects com raiz de agregado única. Ex.: `Order` é raiz; `OrderItem` pertence ao agregado de pedido. Persistência e transações respeitam limites de agregado.

### Auditoria (Audit Trail)
Registro imutável de ações sensíveis (quem, o quê, quando) no painel admin — alterações de preço, estoque, permissões, cancelamentos.

---

## C

### Carrinho (Cart)
Conjunto temporário de itens que o cliente pretende comprar. Pode ser anônimo (sessão/Redis) ou vinculado a usuário autenticado. Não é pedido até o checkout ser confirmado.

### Cashback
Crédito devolvido ao cliente após compra, utilizável em pedidos futuros. Regra de negócio do contexto **Promotion**.

### Categoria (Category)
Nó em árvore hierárquica de classificação de produtos. Suporta subcategorias. Usada para navegação e SEO.

### Checkout
Processo de conversão do carrinho em pedido: endereço, frete, cupom, método de pagamento e confirmação.

### Contexto Delimitado (Bounded Context)
Fronteira explícita de modelo de domínio. Ex.: **Catalog** não conhece detalhes de gateway de pagamento; comunica via eventos ou IDs.

### Cupom (Coupon)
Código promocional com regras (desconto percentual/fixo, validade, uso máximo, valor mínimo). Aplicado no checkout.

---

## E

### Estoque (Inventory)
Quantidade disponível de um SKU. Movimentações (reserva, baixa, reposição) são rastreadas. Estoque baixo gera alerta no dashboard.

---

## F

### Frete (Shipping)
Custo e prazo de entrega calculados com base em CEP, peso/dimensões e transportadora (Correios ou tabela própria).

---

## L

### Loja (Store)
Instância whitelabel configurável: identidade visual, domínio, métodos de pagamento habilitados, políticas. No MVP: uma loja por deploy.

---

## M

### MFA (Multi-Factor Authentication)
Segundo fator de autenticação (TOTP) além de senha, opcional por usuário.

---

## P

### Pagamento (Payment)
Transação financeira vinculada a um pedido. Pode ser PIX, boleto ou cartão. Status independente do status logístico do pedido.

### Pedido (Order)
Compromisso de compra confirmado após checkout. Contém itens, totais, endereço de entrega, status e referência ao pagamento.

### Permissão (Permission)
Ação atômica autorizável no RBAC (ex.: `products:write`, `orders:read`).

### Produto (Product)
Item vendável no catálogo. Possui SKU, preço, descrição, mídia, variações e vínculo a categoria/marca.

### Produto Relacionado
Sugestão de produtos similares ou complementares na página de detalhe.

---

## R

### RBAC (Role-Based Access Control)
Modelo de autorização: usuários recebem **roles**; roles agregam **permissions**.

### Refresh Token
Token de longa duração usado para obter novo access token JWT sem novo login. Rotacionado a cada uso.

### Role (Papel)
Conjunto nomeado de permissões (ex.: `admin`, `customer`, `staff`).

---

## S

### SKU (Stock Keeping Unit)
Identificador único de unidade de estoque. Pode haver variações (tamanho, cor) com SKUs distintos.

### Status do Pedido (Order Status)
Ciclo de vida: `CREATED` → `AWAITING_PAYMENT` → `PAID` → `PROCESSING` → `SHIPPED` → `DELIVERED` | `CANCELLED`.

---

## T

### Tenant
Inquilino lógico em arquitetura multi-loja. No MVP preparado via `tenant_id`; isolamento completo em fase futura.

### Ticket Médio (Average Order Value)
Receita total ÷ número de pedidos no período. Métrica do dashboard.

---

## U

### Unit of Work
Padrão que agrupa múltiplas operações de repositório em uma transação atômica.

### Usuário (User)
Pessoa autenticada na plataforma. Pode ser cliente, funcionário ou admin conforme roles.

---

## V

### Value Object (VO)
Objeto imutável definido por valor, sem identidade própria. Ex.: `Money`, `Email`, `Address`, `CEP`.

### Variação de Produto (Product Variation)
Combinação de atributos (ex.: cor + tamanho) com SKU e preço/estoque próprios.

---

## W

### Whitelabel
Capacidade de rebrandear a plataforma (logo, cores, domínio, banners) sem alterar o núcleo de código.

---

## Termos técnicos (integração)

| Termo | Definição |
|-------|-----------|
| Gateway de Pagamento | Adapter externo (Mercado Pago, Stripe…) que processa cobrança |
| MinIO | Object storage S3-compatible para imagens e assets |
| Presigned URL | URL temporária para upload/download direto no storage |
| Porta (Port) | Interface na camada application que infra implementa |
| Adapter | Implementação concreta de uma porta (ex.: `MercadoPagoPaymentAdapter`) |
| Command | Intenção de alterar estado (CQRS) — ex.: `CreateOrderCommand` |
| Query | Consulta read-only (CQRS) — ex.: `GetProductCatalogQuery` |

---

## Relacionamentos entre termos

```
Store (whitelabel)
  └── Catalog → Product → SKU → Inventory
  └── Cart → Checkout → Order → Payment
  └── Promotion → Coupon / Cashback
  └── Identity → User → Role → Permission
  └── Review (Product + User)
  └── Notification (eventos de Order, Payment)
```
