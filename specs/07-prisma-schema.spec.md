# Spec 07 — Prisma Schema

**Fase:** Persistência  
**Entrada:** Domain model, agregados  
**Saída:** `prisma/schema.prisma`, migration inicial

## Objetivo

Modelar persistência relacional alinhada a agregados sem vazar ORM para o domínio.

## Checklist

- [ ] Tabela por entidade persistida dentro do agregado
- [ ] FKs e cascades coerentes com limites de agregado
- [ ] Enums para estados de ciclo de vida
- [ ] Índices em colunas de busca
- [ ] Migration gerada e aplicável

## Critérios de aceite

- `npx prisma validate` passa
- Nenhum import `@prisma/client` fora de `infrastructure/`
- Mapper plan documentado para cada repositório

## Próximo passo

→ Executar `specs/08-backend.spec.md`
