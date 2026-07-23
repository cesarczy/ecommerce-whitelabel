# Workflow — Pipeline de Desenvolvimento

```mermaid
flowchart LR
  P[Master Prompt] --> S1[01 Discovery]
  S1 --> S2[02 Context]
  S2 --> S3[03 Domain]
  S3 --> S4[04 Use Cases]
  S4 --> S5[05 Ports]
  S5 --> S6[06 Modules]
  S6 --> S7[07 Prisma]
  S7 --> S8[08 Backend]
  S8 --> S9[09 Frontend]
  S9 --> S10[10 Integration]
  S10 --> S11[11 Testing]
  S11 --> S12[12 Harness]
  S12 --> H{PASS?}
  H -->|Sim| D[Entrega]
  H -->|Não| F[Correções]
  F --> S12
```

| Camada | Função | Local |
|--------|--------|-------|
| Rules | Guia contínuo | `.cursor/rules/` |
| Specs | Etapas sequenciais | `specs/` |
| Prompt | Orquestração | `prompts/master-prompt.md` |
| Harness | Validação | `harness/scripts/` |
