# Spec 11 — Testing

**Fase:** Qualidade e regressão  
**Entrada:** Código implementado  
**Saída:** Suite de testes por camada

## Objetivo

Garantir cobertura adequada e testes alinhados à arquitetura hexagonal.

## Pirâmide de testes

| Camada | Tipo | Mock |
|--------|------|------|
| Domain | Unit | Nenhum |
| Application | Unit | Ports |
| Infrastructure | Integration | DB test container |
| Presentation | E2E/API | App completa |
| Frontend | Component + E2E | API mock |

## Checklist

- [ ] Domain: invariantes e VOs 100% testados
- [ ] Use cases: happy path + erros principais
- [ ] Repositories: integração com DB de teste
- [ ] API: supertest nos endpoints MVP
- [ ] CI roda testes em PR

## Critérios de aceite

- Cobertura domain ≥ 80%
- Zero testes que importam Prisma no domain
- Pipeline CI verde

## Próximo passo

→ Executar `specs/12-validation.spec.md`
