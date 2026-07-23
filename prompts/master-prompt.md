# Master Prompt — Pipeline Clean Architecture + DDD

Use este prompt **uma única vez** para conduzir o agente pelas 12 specs em sequência.

---

## Prompt (copie abaixo)

```
Você é um arquiteto de software especialista em Clean Architecture (Robert C. Martin)
e Implementing Domain-Driven Design (Vaughn Vernon).

Execute o pipeline completo deste repositório, spec por spec, em ordem estrita.
Leia e siga AGENTS.md e todas as Rules em .cursor/rules/.

## Contexto do projeto
[DESCREVA AQUI: produto, usuários, stack preferida, restrições]

## Instruções

1. Leia `specs/01-project-discovery.spec.md` e produza todos os artefatos exigidos.
2. Somente após concluir spec 01, avance para spec 02, e assim até spec 12.
3. Não pule etapas. Não implemente backend antes do domain model.
4. Aplique os templates em `templates/` quando aplicável.
5. Respeite a regra de dependência: domain no centro, sem imports de framework no domínio.
6. Ao finalizar spec 12, execute: `./harness/scripts/run-harness.sh`
7. Corrija todas as violações e reexecute até PASS.

## Formato de progresso

Após cada spec, reporte:
- ✅ Spec NN — [nome] — concluída
- Artefatos gerados: [lista de paths]
- Decisões tomadas: [bullets]
- Próximo: Spec NN+1

## Stack padrão (ajuste se necessário)
- TypeScript, Node.js
- Prisma + PostgreSQL
- Express ou Fastify
- React (frontend)
- Vitest/Jest

Comece agora pela Spec 01.
```

---

## Variantes

### MVP rápido
Adicione: `Limite escopo ao MVP definido na spec 01. Postergue frontend para iteração 2.`

### Só backend
Adicione: `Pule spec 09 (frontend). Marque como N/A no relatório final.`

### Projeto existente (brownfield)
Adicione: `Faça gap analysis antes da spec 03. Não reescreva código funcional sem justificativa.`
