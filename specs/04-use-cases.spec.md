# Spec 04 — Use Cases

**Fase:** Application layer  
**Entrada:** Domain model, user stories do discovery  
**Saída:** `src/modules/*/application/**`

## Objetivo

Definir casos de uso como orquestradores — uma classe por ação do sistema.

## Checklist

- [ ] Um use case por operação significativa
- [ ] Input/Output DTOs tipados
- [ ] Dependências via ports (interfaces)
- [ ] Coleta e publicação de domain events pós-persistência
- [ ] Tratamento de not-found e conflitos
- [ ] Testes com mocks de ports

## Critérios de aceite

- Use cases não importam Express, Prisma ou React
- Fluxos felizes e de erro testados
- DTOs separados de entidades de domínio

## Próximo passo

→ Executar `specs/05-ports-adapters.spec.md`
