# Spec 03 — Domain Model

**Fase:** Modelagem tática DDD  
**Entrada:** `docs/context-map.md`  
**Saída:** `src/modules/*/domain/**`

## Objetivo

Implementar agregados, entidades, value objects, eventos e exceções de domínio.

## Checklist por agregado

- [ ] Aggregate root identificado
- [ ] Invariantes documentadas e enforced no código
- [ ] Value objects para conceitos com validação
- [ ] Factory/create methods; reconstitute para rehydration
- [ ] Domain events para fatos relevantes
- [ ] DomainError para violações de regra
- [ ] Referências cross-aggregate por ID
- [ ] Testes unitários de invariantes

## Critérios de aceite

- Zero imports de framework/ORM no domain
- Cobertura de testes ≥ 80% em domain/
- Cada agregado tem repositório planejado (interface na spec 05)

## Próximo passo

→ Executar `specs/04-use-cases.spec.md`
