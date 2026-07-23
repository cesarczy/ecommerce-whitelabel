# Cursor Clean Architecture + DDD Kit

Framework de desenvolvimento assistido por IA baseado em **Clean Architecture** (Robert C. Martin) e **Implementing Domain-Driven Design** (Vaughn Vernon).

Transforma padrões arquiteturais em **Rules**, **Prompts**, **Specs** e **Harness** para execução previsível no Cursor, Codex e assistentes compatíveis.

## Estrutura

```
cursor-clean-ddd-kit/
├── .cursor/
│   ├── rules/              # 15 regras especializadas por padrão
│   └── skills/             # Skill do pipeline de specs
├── prompts/                # Prompt mestre (dispara as 12 specs)
├── specs/                  # 12 especificações sequenciais
├── harness/                # Validação automatizada de arquitetura
├── docs/                   # Documentação e mapeamento de padrões
├── templates/              # Scaffolds reutilizáveis
└── references/             # Fontes bibliográficas
```

## Fluxo de uso

1. Copie este kit para seu projeto (ou abra como base).
2. Execute o prompt mestre: `prompts/master-prompt.md`
3. O agente executa as **12 specs em sequência** (01 → 12).
4. Ao final, rode o harness: `./harness/scripts/run-harness.sh`
5. Corrija violações reportadas e revalide até passar.

## As 12 Specs

| # | Spec | Objetivo |
|---|------|----------|
| 01 | project-discovery | Contexto, requisitos, glossário |
| 02 | bounded-context | Contextos delimitados e mapa |
| 03 | domain-model | Entidades, VOs, agregados, eventos |
| 04 | use-cases | Casos de uso e portas de entrada |
| 05 | ports-adapters | Portas, adaptadores, inversão de dependência |
| 06 | module-structure | Estrutura de pastas e módulos |
| 07 | prisma-schema | Modelagem relacional com Prisma |
| 08 | backend | Implementação da camada de aplicação/infra |
| 09 | frontend | UI, state, integração com API |
| 10 | integration | Wiring, DI, composição de módulos |
| 11 | testing | Testes por camada e contrato |
| 12 | validation | Harness final e checklist de entrega |

## Fontes

- *Clean Architecture* — Robert C. Martin
- *Implementing Domain-Driven Design* — Vaughn Vernon

Ver `references/` e `docs/sources/`.
