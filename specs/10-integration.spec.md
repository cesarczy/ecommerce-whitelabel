# Spec 10 — Integration

**Fase:** Composição e wiring  
**Entrada:** Módulos, adapters, use cases  
**Saída:** Bootstrap completo, DI, event handlers cross-module

## Objetivo

Conectar todas as peças: DI container, rotas, handlers de eventos, configuração.

## Checklist

- [ ] `src/main.ts` ou `src/composition-root.ts` com wiring explícito
- [ ] Registro de rotas HTTP
- [ ] Event handlers registrados no EventBus
- [ ] Config centralizada (`config/`)
- [ ] Graceful shutdown
- [ ] Integração cross-context via eventos/API conforme context map
- [ ] Smoke test end-to-end automatizado

## Critérios de aceite

- App inicia sem erros de DI
- Fluxo MVP completo funciona via API + UI
- Eventos cross-context processados

## Próximo passo

→ Executar `specs/11-testing.spec.md`
