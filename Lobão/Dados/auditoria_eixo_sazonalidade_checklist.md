# Checklist Final por Etapa — Eixo 3 Sazonalidade

| Etapa | Status | Output existe | Granularidade correta | Métricas corretas | Gráficos/Tabelas | Insights utilizáveis | Observação |
|---|---|---|---|---|---|---|---|
| S-A1 | PARTIAL | Não (`sa1_outputs` ausente) | Sim (validado por recomputação) | Sim (sanity check) | Não auditável (ficheiros ausentes) | Parcial | Regerar artefactos da etapa |
| S-A2 | OK | Sim | Sim (`Country x Month`) | Sim | Sim | Sim | Sem correções críticas |
| S-A3 | OK | Sim | Sim (`Main_Category x Month`) | Sim | Sim | Sim | Explicitar no slide que média anual está ponderada por linhas |
| S-A4 | OK | Sim | Sim (`Main_Category x Month`) | Sim | Sim | Sim | Sem correções críticas |

## Itens transversais
- [x] Base de trabalho correta (13 colunas esperadas)
- [x] Intervalo temporal coerente (2020-01-01 a 2025-12-31)
- [x] `Gross_Profit` validado
- [x] Margem agregada por quociente de somas validada
- [x] Exclusões de nulos aplicadas de forma específica por análise
- [ ] `S-A1` com artefactos exportados
