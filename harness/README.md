# Harness — Validação automatizada

```bash
chmod +x harness/scripts/*.sh   # primeira vez
./harness/scripts/run-harness.sh
```

| Script | Verifica |
|--------|----------|
| `run-harness.sh` | Orquestrador — exit 0 = PASS |
| `check-layer-dependencies.sh` | Domain sem imports proibidos |
| `check-ddd-compliance.sh` | Naming use-case, sem service no domain |
| `check-prisma-schema.sh` | Prisma isolado em infrastructure |
| `check-architecture.sh` | Estrutura mínima kit/módulos |

Configuração: `config/checks.yaml`
