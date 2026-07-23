---
name: run-spec-pipeline
description: >-
  Executa o pipeline de 12 specs Clean Architecture + DDD em sequência.
  Use quando o usuário pedir para iniciar desenvolvimento guiado por specs,
  aplicar DDD/Clean Architecture, ou rodar o master prompt deste kit.
---

# Run Spec Pipeline

## Quando usar

- Novo projeto ou feature grande com arquitetura DDD/CA
- Usuário referencia `master-prompt.md`, specs/, ou harness

## Workflow

1. Ler `AGENTS.md`
2. Executar specs `01` → `12` em `specs/` **sem pular**
3. Aplicar rules em `.cursor/rules/` automaticamente
4. Usar templates em `templates/` para scaffolding
5. Ao concluir spec 12, rodar `./harness/scripts/run-harness.sh`
6. Iterar correções até harness PASS

## Progresso

Reportar após cada spec:

```
✅ Spec NN — [nome]
Artefatos: [paths]
Decisões: [bullets]
→ Próximo: Spec NN+1
```

## Referências

- Padrões: `docs/patterns/`
- Prompt mestre: `prompts/master-prompt.md`
- Config harness: `harness/config/checks.yaml`
