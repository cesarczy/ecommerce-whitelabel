# Spec 06 — Module Structure

**Fase:** Organização física  
**Entrada:** Context map, ports, domain  
**Saída:** Árvore completa de pastas, barrels, READMEs por módulo

## Objetivo

Materializar estrutura de módulos alinhada a Clean Architecture e bounded contexts.

## Checklist

- [ ] `src/modules/<context>/` com domain, application, infrastructure, presentation
- [ ] `src/shared/` com primitives compartilhados (mínimo)
- [ ] `index.ts` barrels nas pastas públicas
- [ ] Path aliases no tsconfig (`@orders/domain`, etc.)
- [ ] README.md por módulo explicando responsabilidade

## Critérios de aceite

- Harness de camadas passa (sem imports invertidos)
- Estrutura navegável por dev novo em < 5 min
- Nenhum arquivo solto na raiz de `src/` exceto `main.ts`

## Próximo passo

→ Executar `specs/07-prisma-schema.spec.md`
