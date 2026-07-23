# Clean Architecture — Resumo de Padrões

> Fonte: *Clean Architecture*, Robert C. Martin

## Camadas

```
┌─────────────────────────────────────────────┐
│  Frameworks & Drivers (DB, Web, UI)       │
├─────────────────────────────────────────────┤
│  Interface Adapters (Controllers, Gateways) │
├─────────────────────────────────────────────┤
│  Application Business Rules (Use Cases)     │
├─────────────────────────────────────────────┤
│  Enterprise Business Rules (Entities)       │
└─────────────────────────────────────────────┘
         ↑ dependências apontam para dentro ↑
```

## Mapeamento

| Componente | Rule | Spec |
|------------|------|------|
| Entities | `ddd-aggregates.mdc` | 03 |
| Use Cases | `use-cases.mdc` | 04 |
| Adapters | `ports-adapters.mdc` | 05, 08, 09 |
| Frameworks | `backend-development.mdc` | 07, 08 |
