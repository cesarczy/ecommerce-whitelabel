# Spec 08 — Backend Implementation

**Fase:** Infraestrutura + Presentation HTTP  
**Entrada:** Ports, Prisma schema, use cases  
**Saída:** Repositórios, mappers, controllers, `src/main.ts`

## Objetivo

Implementar adapters concretos e expor API HTTP fina sobre use cases.

## Checklist

- [ ] Repository implementations com mappers
- [ ] EventBus / adapters externos
- [ ] HTTP controllers (validação → use case → response)
- [ ] Error handler global (DomainError → 4xx)
- [ ] Health check endpoint
- [ ] Variáveis de ambiente documentadas (`.env.example`)
- [ ] Testes de integração para repositórios críticos

## Critérios de aceite

- API funcional end-to-end para fluxo MVP
- Controllers < 30 linhas por handler
- Logs estruturados com request ID

## Próximo passo

→ Executar `specs/09-frontend.spec.md`
