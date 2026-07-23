# Frontend — E-commerce Whitelabel

Angular 20 + Material + NGXS + TailwindCSS.

## Setup

```bash
cd frontend
npm install
npm start
```

App: http://localhost:4200  
API: http://localhost:8000

## Estrutura

```
src/app/
├── core/       # Auth, API, NGXS, guards, interceptors
├── shared/     # Componentes compartilhados
├── layout/     # Shell whitelabel
├── pages/      # Loja (login, produtos, carrinho, checkout)
└── admin/      # Painel administrativo
```

## Fluxo MVP

1. Cadastro / Login
2. Listar produtos
3. Adicionar ao carrinho
4. Checkout (autenticado)
5. Admin dashboard
