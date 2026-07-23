# AGENTS.md — Instruções para agentes de IA

## Missão

Aplicar Clean Architecture e DDD de forma consistente em todo ciclo de desenvolvimento, seguindo Rules, Specs e Harness deste repositório.

## Ordem de execução obrigatória

1. Ler `prompts/master-prompt.md`
2. Executar specs `specs/01-*.md` até `specs/12-*.md` **em sequência**
3. Não pular specs; cada uma produz artefatos consumidos pela próxima
4. Ao concluir implementação, executar `./harness/scripts/run-harness.sh`
5. Corrigir falhas e reexecutar até aprovação

## Regras ativas

As regras em `.cursor/rules/` aplicam-se automaticamente conforme globs. Respeite:

- Dependências apontam **sempre para dentro** (domínio no centro)
- Domínio **nunca** importa infraestrutura, framework ou ORM
- Agregados protegem invariantes; persistência via repositórios
- Prisma/schema fica na camada de infraestrutura; mapeamento explícito

## Saídas esperadas por spec

| Spec | Artefatos |
|------|-----------|
| 01 | `docs/discovery.md`, glossário |
| 02 | `docs/context-map.md` |
| 03 | `src/domain/**` |
| 04 | `src/application/**` |
| 05 | `src/ports/**`, interfaces |
| 06 | Estrutura de módulos completa |
| 07 | `prisma/schema.prisma` |
| 08 | `src/infrastructure/**`, handlers |
| 09 | `src/presentation/**` ou `frontend/**` |
| 10 | `src/main.ts`, módulos DI |
| 11 | `tests/**` |
| 12 | Relatório harness + checklist |

## Proibições

- Lógica de negócio em controllers, components ou schema Prisma
- Entidades de domínio anêmicas sem comportamento
- Use cases que conhecem detalhes de HTTP, Prisma ou React
- Imports circulares entre camadas

## Validação

O harness verifica: dependências entre camadas, convenções de nomenclatura, presença de testes mínimos e conformidade DDD/CA.
