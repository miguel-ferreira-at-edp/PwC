# Resumo Executivo — Auditoria do Eixo 3 (Sazonalidade)

## Diagnóstico rápido
- A base `sales_data_sazonalidade_work.csv` está correta e consistente (2020-2025, fórmulas validadas, sem duplicados de `Sales_Order_ID`).
- `S-A2`, `S-A3` e `S-A4` estão metodologicamente corretas e com outputs prontos para uso.
- `S-A1` está com lacuna de artefactos (`sa1_outputs` ausente), portanto a etapa fica **PARTIAL**.

## Estado por etapa
- S-A1: **PARTIAL** (falta export da etapa)
- S-A2: **OK**
- S-A3: **OK**
- S-A4: **OK**

## Mensagem integrada
- O padrão sazonal é claro: pico em dezembro e baixa em maio/junho.
- O ticket médio tende a subir no pico em parte dos países, mas a margem não acompanha na mesma intensidade.
- O custo de produção não mostra subida forte na peak season, sugerindo que a pressão de margem está mais em mix/preço/promos/logística do que em produção pura.

## Correção mínima pendente
1. Regerar `sa1_outputs` (CSVs + PNGs obrigatórios).
2. Consolidar todos os outputs num único diretório final.
3. Incluir 1 nota metodológica com fórmulas/exclusões/definição de sazonalidade.
