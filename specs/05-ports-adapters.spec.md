# Spec 05 — Ports & Adapters

**Fase:** Inversão de dependência  
**Entrada:** Use cases, requisitos de infra  
**Saída:** `application/ports/**`, contratos de adapters

## Objetivo

Definir todas as portas (interfaces) e especificar adapters necessários.

## Checklist

- [ ] Repository port por aggregate root
- [ ] Ports para serviços externos (email, pagamento, storage)
- [ ] EventBus / UnitOfWork se aplicável
- [ ] Clock port para testabilidade de datas
- [ ] Documentação de cada adapter planejado

## Critérios de aceite

- Interfaces em `application/ports/` sem implementação
- Nenhum adapter concreto importado em domain/application
- DI plan documentado para spec 10

## Próximo passo

→ Executar `specs/06-module-structure.spec.md`
