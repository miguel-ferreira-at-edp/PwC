# Auditoria Final — Eixo 3: Sazonalidade (SkiWell Sports)

## 1. Resumo executivo
A auditoria confirma que a base `sales_data_sazonalidade_work.csv` está tecnicamente consistente e que as análises `S-A2`, `S-A3` e `S-A4` foram executadas com metodologia adequada e outputs reutilizáveis. O principal gap atual é a ausência dos artefactos de `S-A1` (`sa1_outputs`), que impede rastreabilidade total da etapa.

Mesmo sem os ficheiros da `S-A1`, um sanity check independente sobre a base confirma padrão sazonal forte: pico de revenue em dezembro (mês 12) e vale em maio (mês 5), coerente com os resultados de `S-A4` por categoria.

Conclusão geral: o eixo sazonalidade está robusto para narrativa executiva, com uma correção mínima pendente (regerar/exportar `S-A1`).

## 2. Estado da auditoria (OK / PARTIAL / MISSING por etapa)

| Etapa | Estado | Diagnóstico curto |
|---|---|---|
| S-A1 — Revenue e Volume por Mês (Global + Região) | PARTIAL | `sa1_outputs` não existe; cálculos e história sazonal foram validados por recomputação rápida, mas faltam artefactos exportados. |
| S-A2 — Sales Price médio por País | OK | Métricas e rankings corretos, gráficos e CSVs presentes. |
| S-A3 — Production Cost por Mês | OK | Agregação e desvios corretos; interpretação JIT possível com ressalvas. |
| S-A4 — Sazonalidade por Categoria | OK | Índice sazonal e outputs corretos; coerência elevada com história global. |

## 3. Avaliação da preparação dos dados

### 3.1 Estrutura e cobertura de colunas
A base contém exatamente as 13 colunas esperadas:
- `Order_Date, Year, Region, Country, Main_Category, Sales_Order_ID, Sales_Price, Production_Cost`
- `Month, Month_Name, YearMonth, Gross_Profit, Gross_Margin_pct`

Shape validado: `147511 x 13`.

### 3.2 Intervalo temporal, tipos e nulos
- Intervalo efetivo: `2020-01-01` a `2025-12-31`.
- `Year` cobre `2020..2025` e `YearMonth` cobre 72 meses.
- `Country` nulo: 300 linhas.
- `Main_Category` nulo: 17 linhas.
- `Sales_Order_ID` sem duplicados (`147511` únicos em `147511` linhas).

Observação técnica: em CSV, `Order_Date` lê como texto por default; isso é esperado e foi convertido para datetime nas análises.

### 3.3 Validação das fórmulas base
- `Gross_Profit = Sales_Price - Production_Cost`: validado (erro numérico apenas residual de ponto flutuante).
- `Gross_Margin_pct` linha a linha: validado.

### 3.4 Margem agregada (metodologia)
Nas etapas auditadas com margem (`S-A2` e `S-A4`), a margem foi recalculada corretamente como:
- `sum(Gross_Profit) / sum(Sales_Price) * 100`

Não foi identificado uso indevido de média simples de margens linha a linha nas tabelas agregadas.

### 3.5 Ficheiros desnecessários
Não há evidência de ficheiros supérfluos gerados no eixo; existem apenas:
- base de trabalho
- pastas de outputs `sa2_outputs`, `sa3_outputs`, `sa4_outputs`

Gap: `sa1_outputs` ausente.

## 4. Insights finais por etapa

### S-A1
#### A. Objetivo da etapa
Identificar picos/vales mensais globais e por região, comparando padrões sazonais geográficos.

#### B. Inputs usados
Esperado: `sales_data_sazonalidade_work.csv` com colunas `Month, Region, Sales_Order_ID, Sales_Price, Gross_Profit`.

#### C. Cálculos e métricas
Esperado e metodologicamente correto:
- `Revenue = sum(Sales_Price)`
- `Orders = count(Sales_Order_ID)`
- `Gross_Profit = sum(Gross_Profit)`
- `Gross_Margin_pct = Gross_Profit / Revenue * 100`
- `Seasonality_Index = Revenue_mes / média_mensal_da_região * 100`

#### D. Outputs produzidos
Estado atual: **não encontrados** (`sa1_outputs` inexistente).

#### E. Validação metodológica
**PARTIAL**: sem artefactos não há audit trail completo. Contudo, recomputação rápida confirma:
- pico global de revenue: mês `12`
- vale global de revenue: mês `5`
- pico de índice sazonal por região também em `12`.

#### F. Insights extraídos
- Sazonalidade forte e sincronizada entre regiões (pico no fim do ano).

#### G. Lacunas / melhorias
- Correção mínima: regenerar 4 ficheiros de `S-A1` (2 CSV + 2/3 PNG + resumo por região).

### S-A2
#### A. Objetivo da etapa
Medir variação sazonal de preço médio por país e seu efeito na margem.

#### B. Inputs usados
- `sales_data_sazonalidade_work.csv`
- Exclusão apenas de `Country` nulo.

#### C. Cálculos e métricas
Corretos e aderentes ao pedido:
- Agregação `Country x Month` com `Revenue, Orders, Avg_Ticket, Gross_Profit, Gross_Margin_pct`.
- `Peak_Season = [11,12,1,2,3]`
- `Low_Season = [5,6,7,8,9]`
- `Delta_Ticket_pct`, `Delta_Margin_pp`.

#### D. Outputs produzidos
CSV:
- `sa2_country_month_aggregated.csv`
- `sa2_country_peak_low_comparison.csv`
- `sa2_ranking_delta_ticket_pct.csv`
- `sa2_ranking_delta_margin_pp.csv`
PNG:
- `sa2_top_revenue_avg_ticket_peak_vs_low.png`
- `sa2_top_revenue_delta_margin_pp.png`

#### E. Validação metodológica
**OK**. Consistência numérica validada entre colunas derivadas e fórmulas.

#### F. Insights extraídos
- 7/11 países com `Delta_Ticket_pct > 0`.
- Maiores altas de ticket: Andorra (+6.88%), Switzerland (+3.45%), China (+2.24%).
- Margem melhora em 7 países, mas com magnitudes pequenas.
- Espanha e Itália apresentam compressão de margem no pico.

#### G. Lacunas / melhorias
- Acrescentar segmentação por ano para verificar estabilidade dos deltas.
- Incluir intervalo de confiança / sensibilidade para países com menor base de revenue.

### S-A3
#### A. Objetivo da etapa
Testar se custo médio de produção sobe em meses de pico, sugerindo produção tardia (JIT sob pressão).

#### B. Inputs usados
- `sales_data_sazonalidade_work.csv`
- Exclusão apenas de `Main_Category` nulo.

#### C. Cálculos e métricas
Corretos:
- Agregação `Main_Category x Month`:
  - `Avg_Production_Cost = mean(Production_Cost)`
  - `Revenue = sum(Sales_Price)`
  - `Orders = count(Sales_Order_ID)`
- Média anual por categoria e desvio mensal vs média.

#### D. Outputs produzidos
CSV:
- `sa3_month_main_category_aggregated.csv`
- `sa3_top_cost_months_by_category.csv`
- `sa3_peak_deviation_vs_average_by_category.csv`
PNG:
- `sa3_avg_production_cost_by_month_category.png`

#### E. Validação metodológica
**OK** com ressalva interpretativa:
- A fórmula está correta.
- A “média anual” foi calculada com ponderação por volume de linhas (não média simples dos 12 meses). Isso é defensável, mas convém explicitar no slide para evitar ambiguidade.

#### F. Insights extraídos
- Picos de custo: agosto (Accessories/Technical equipment) e março (Clothing).
- Desvios de pico vs média anual modestos (~1.2% a ~2.6%).
- Em média, Peak Season não encarece custo de produção de forma forte.

#### G. Lacunas / melhorias
- Fazer teste de defasagem (lag) custo -> vendas para reforçar ou refutar hipótese JIT.
- Separar custo por país/fábrica, se disponível.

### S-A4
#### A. Objetivo da etapa
Comparar padrões sazonais entre categorias e verificar convergência/divergência de picos.

#### B. Inputs usados
- `sales_data_sazonalidade_work.csv`
- Exclusão apenas de `Main_Category` nulo.

#### C. Cálculos e métricas
Corretos:
- Agregação `Main_Category x Month` com revenue, orders, gross profit e margem.
- `Seasonality_Index = Revenue_mes / média_mensal_da_categoria * 100`.

#### D. Outputs produzidos
CSV:
- `sa4_main_category_month_seasonality.csv`
- `sa4_category_peak_valley_amplitude.csv`
PNG:
- `sa4_heatmap_month_main_category_seasonality_index.png`
- `sa4_line_seasonality_index_by_main_category.png`

#### E. Validação metodológica
**OK**. Índice sazonal e margem agregada validados.

#### F. Insights extraídos
- Todas as categorias têm pico em dezembro.
- Vales em maio/junho.
- Amplitude sazonal relevante em todas as categorias (~50–56 pontos).

#### G. Lacunas / melhorias
- Incluir corte `Categoria x Região` para priorização operacional mais acionável.

## 5. História integrada do eixo sazonalidade
- `S-A1` (sanity check) e `S-A4` contam a mesma história: pico sazonal em dezembro e baixa em maio/junho.
- `S-A2` mostra que o efeito sazonal aparece mais no preço/ticket do que na margem.
- `S-A3` indica que custo de produção não sobe de forma clara na Peak Season, logo a variação de margem parece mais ligada a mix, descontos e/ou custos fora da produção (ex.: logística/comercial).

Conclusão integrada: há sazonalidade forte da procura, relativamente sincronizada, com necessidade de planeamento pré-pico e disciplina de pricing por país.

## 6. Principais constrangimentos operacionais encontrados
- Forte concentração de procura no fim do ano (risco de ruptura/capacidade).
- Compressão de margem em alguns países durante pico (execução comercial heterogénea).
- Sinais de pico de custo fora da época alta (potencial desalinhamento no planeamento de produção).

## 7. Recomendações operacionais derivadas do eixo sazonalidade
1. Planeamento S&OP por janela sazonal (pré-build de inventário antes de dezembro).
2. Playbook de pricing por país para Peak Season (evitar erosão de margem em mercados críticos).
3. Revisão de calendário de produção e compras para reduzir picos de custo fora da janela ótima.
4. Dashboard mensal com `Seasonality Index`, `Avg Ticket`, `Gross Margin` por país e categoria.
5. Stress-test de capacidade logística/stock para novembro-dezembro.

## 8. Pressupostos e limitações
### Pressupostos usados
- `Country` nulo foi excluído **apenas** em análises por país (`S-A2`).
- `Main_Category` nulo foi excluído **apenas** em análises por categoria (`S-A3`, `S-A4`).
- Peak/Low season em `S-A2`:
  - Peak: `[11,12,1,2,3]`
  - Low: `[5,6,7,8,9]`
- Margens agregadas recalculadas por quociente de somas.

### Limitações
- `S-A1` sem artefactos exportados (lacuna de reprodutibilidade da etapa).
- Agregação “sobre todos os anos” pode ocultar mudanças estruturais anuais.
- Sem variáveis de transporte/expedição neste eixo, limita explicação causal completa da margem.

## 9. O que está pronto para slide
### Visuais mais fortes
1. `sa4_heatmap_month_main_category_seasonality_index.png`
2. `sa2_top_revenue_avg_ticket_peak_vs_low.png`
3. `sa3_avg_production_cost_by_month_category.png`

### Visuais descartáveis (ou só para apêndice)
- `sa2_top_revenue_delta_margin_pp.png` (manter como suporte técnico, não como visual principal).

### Mensagens mais slide-ready
- “Pico sazonal comum em dezembro em todas as categorias e regiões.”
- “Preço médio sobe no pico em parte dos mercados, mas ganho de margem é limitado.”
- “Não há evidência forte de encarecimento de produção na Peak Season.”

## 10. O que ainda precisa de correção
1. Recriar `sa1_outputs` (CSVs e PNGs da etapa S-A1) para fechar auditoria com rastreabilidade completa.
2. Padronizar diretório final de outputs (evitar ambiguidade entre `data/` e `Lobão/Dados/`).
3. Adicionar nota metodológica única (README curto) com fórmulas, exclusões e definição de sazonalidade.

---

## 5 bullets finais prontos para apresentação
- A sazonalidade da SkiWell é forte e sincronizada: dezembro é o pico estrutural de revenue.
- O vale sazonal concentra-se em maio/junho, criando janela para manutenção, formação e otimização de capacidade.
- O efeito sazonal é mais evidente no ticket médio do que na margem final.
- Alguns países perdem margem no pico, sugerindo necessidade de governance de pricing e promoções.
- Custos de produção não sobem claramente no pico, reforçando foco em mix/comercial/logística para proteger rentabilidade.

## 3 títulos executivos possíveis para o slide
1. **Sazonalidade Forte, Margem Fragil em Mercados-Chave**
2. **Dezembro Concentra a Procura: Onde Ganhar (ou Perder) Rentabilidade**
3. **SkiWell: Pico de Volume Não Garante Pico de Margem**
