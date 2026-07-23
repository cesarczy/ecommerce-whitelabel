# Spec 09 — Frontend

**Fase:** Interface do usuário  
**Entrada:** API contracts, user journeys  
**Saída:** `frontend/**` ou `src/presentation/web/**`

## Objetivo

Implementar UI desacoplada consumindo API via client tipado.

## Checklist

- [ ] Feature folders por capacidade de usuário
- [ ] Hooks para data fetching e mutations
- [ ] Componentes UI dumb em `shared/ui`
- [ ] Tratamento loading/error/empty
- [ ] Validação de formulário (UX)
- [ ] Tipos alinhados aos DTOs da API
- [ ] Testes de componentes críticos

## Critérios de aceite

- Nenhuma regra de negócio autoritativa só no client
- Fluxo MVP navegável end-to-end
- Acessibilidade básica (labels, focus)

## Próximo passo

→ Executar `specs/10-integration.spec.md`
