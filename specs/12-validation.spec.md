# Spec 12 — Validation (Harness)

**Fase:** Conformidade final  
**Entrada:** Projeto completo  
**Saída:** Relatório harness, checklist de entrega

## Objetivo

Validar arquitetura, qualidade e conformidade antes da entrega via harness automatizado.

## Execução

```bash
./harness/scripts/run-harness.sh
```

## Checklist manual + automatizado

- [ ] Harness passa sem erros
- [ ] Nenhum import proibido (domain → prisma/express/react)
- [ ] Context map atualizado
- [ ] README do projeto com setup
- [ ] `.env.example` completo
- [ ] Migrations aplicáveis do zero
- [ ] Demo do fluxo MVP registrada

## Critérios de aceite

- `./harness/scripts/run-harness.sh` exit code 0
- Todas specs marcadas concluídas
- Projeto reproduzível por terceiro seguindo README

## Fim do pipeline

Pipeline concluído. Iterar apenas via change requests documentadas.
