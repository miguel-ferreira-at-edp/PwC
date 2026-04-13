# Relatório Final — Eixo 3: Sazonalidade

## 1. Resumo executivo
A análise consolidada do eixo de sazonalidade confirma um padrão temporal robusto na SkiWell: pico de procura em dezembro e baixa em maio/junho, consistente globalmente, por região e por categoria.

Do lado comercial, em vários países o ticket médio sobe na peak season, mas a margem não melhora na mesma intensidade (e em alguns mercados até piora). Do lado produtivo, os custos médios de produção não sobem de forma clara na peak season, o que enfraquece a hipótese de pressão generalizada de produção tardia (just-in-time) como causa central da erosão de margem.

Mensagem executiva: a sazonalidade da procura é forte e previsível; o principal risco para rentabilidade parece estar mais em pricing/mix e execução operacional por mercado do que em inflação sazonal de custo de produção.

## 2. Metodologia resumida
- Fonte principal: `sales_data_sazonalidade_work.csv`.
- Consolidação feita a partir dos outputs já existentes em `sa1_outputs`, `sa2_outputs`, `sa3_outputs`, `sa4_outputs`.
- Período agregado: 2020-2025, com agregação mensal (jan-dez) sobre todos os anos.
- Regras-chave:
  - `Revenue = sum(Sales_Price)`
  - `Orders = count(Sales_Order_ID)`
  - `Gross_Profit = sum(Gross_Profit)`
  - `Gross_Margin_pct (agregado) = Gross_Profit / Revenue * 100`
  - `Seasonality_Index = Revenue_mes / média_mensal_do_grupo * 100`
- Exclusões específicas:
  - `Country` nulo apenas em análises por país (S-A2)
  - `Main_Category` nulo apenas em análises por categoria (S-A3 e S-A4)

## 3. Resultados por etapa

### 3.1 S-A1 — Revenue e Volume por Mês (Global e por Região)
**Objetivo:** identificar picos/vales sazonais e comparar padrão entre regiões.

**Principais outputs usados:**
- `sa1_global_month_aggregated.csv`
- `sa1_region_month_aggregated.csv`
- `sa1_region_seasonality_index.csv`
- `sa1_region_peak_valley_summary.csv`
- `sa1_global_revenue_by_month.png`
- `sa1_global_orders_by_month.png`
- `sa1_region_seasonality_heatmap.png`

**Principais achados:**
- Revenue global: pico em dezembro (`3,343,979`) e vale em maio (`1,999,960`).
- Orders globais: pico em dezembro (`16,530`) e vale em maio (`9,856`).
- Picos regionais também em dezembro:
  - Asia: índice 132.64
  - Europe: índice 134.85
  - North America: índice 135.67

**Implicações operacionais:**
- Planeamento de capacidade/logística deve ser orientado para novembro-dezembro.
- Maio/junho é janela natural para manutenção, formação e ajuste de inventário.

### 3.2 S-A2 — Variação sazonal do Sales Price médio por País
**Objetivo:** testar variação de preço médio entre pico e baixa estação e impacto em margem.

**Principais outputs usados:**
- `sa2_country_peak_low_comparison.csv`
- `sa2_ranking_delta_ticket_pct.csv`
- `sa2_ranking_delta_margin_pp.csv`
- gráficos de top países por revenue

**Principais achados:**
- 7/11 países com `Delta_Ticket_pct > 0`; 4/11 com queda.
- Top altas de ticket no pico: Andorra (+6.88%), Switzerland (+3.45%), China (+2.24%).
- Margem: 7/11 melhoram, 4/11 pioram.
- Piores deltas de margem: Spain (-0.23 pp), Italy (-0.15 pp), Switzerland (-0.03 pp).

**Validação da conclusão:**
- Conclusão faz sentido: impacto sazonal de preço existe, mas efeito em margem é heterogéneo e menor.

**Implicações operacionais:**
- Necessário playbook de pricing por país na peak season.
- Mercados com erosão de margem pedem revisão de descontos, mix e condições comerciais.

### 3.3 S-A3 — Production Cost por Mês (indício de JIT)
**Objetivo:** avaliar se custo de produção sobe no pico de procura, sugerindo produção tardia.

**Principais outputs usados:**
- `sa3_month_main_category_aggregated.csv`
- `sa3_peak_deviation_vs_average_by_category.csv`
- `sa3_top_cost_months_by_category.csv`
- `sa3_avg_production_cost_by_month_category.png`

**Principais achados:**
- Picos de custo por categoria:
  - Accessories: agosto (+2.58% vs média anual)
  - Clothing: março (+1.18%)
  - Technical equipment: agosto (+1.63%)
- Comparação peak vs low season no custo médio:
  - Accessories: -0.65%
  - Clothing: +0.07%
  - Technical equipment: -0.77%

**Validação da conclusão:**
- A hipótese de subida de custo generalizada na peak season não é fortemente suportada.

**Implicações operacionais:**
- O foco de margem não deve recair apenas em custo de produção sazonal.
- Priorizar análise de mix, pricing e custos logísticos/comerciais.

### 3.4 S-A4 — Sazonalidade por Categoria de Produto
**Objetivo:** verificar convergência/divergência de padrão sazonal entre categorias.

**Principais outputs usados:**
- `sa4_main_category_month_seasonality.csv`
- `sa4_category_peak_valley_amplitude.csv`
- `sa4_heatmap_month_main_category_seasonality_index.png`
- `sa4_line_seasonality_index_by_main_category.png`

**Principais achados:**
- Todas as categorias têm pico em dezembro.
- Vales em maio/junho.
- Amplitude sazonal relevante:
  - Accessories: 56.42
  - Clothing: 50.73
  - Technical equipment: 56.38

**Validação da conclusão:**
- Conclusão robusta e coerente com S-A1.

**Implicações operacionais:**
- Planeamento inter-categorias pode ser sincronizado para pico de dezembro.
- Vales sazonais permitem redistribuição de capacidade e ações de eficiência.

## 4. História integrada do eixo sazonalidade
A história das quatro etapas é coerente:
- S-A1 e S-A4 mostram sazonalidade forte e alinhada (pico em dezembro).
- S-A2 mostra que, embora o ticket suba em vários países, a margem não acompanha de forma uniforme.
- S-A3 mostra que custo de produção não explica sozinho a dinâmica de margem no pico.

Narrativa final: a SkiWell enfrenta um ciclo sazonal previsível de procura; o desafio central de rentabilidade no pico parece ser execução comercial/operacional por mercado (pricing, mix e logística), e não apenas custo produtivo.

## 5. Principais constrangimentos operacionais identificados
1. Forte concentração de volume em novembro-dezembro, pressionando capacidade e serviço.
2. Erosão de margem em alguns países na peak season, apesar de dinâmica de procura favorável.
3. Volatilidade sazonal elevada por categoria, exigindo planeamento fino de inventário.
4. Sinal limitado de custo produtivo no pico, dificultando explicações simplistas de rentabilidade.

## 6. Recomendações operacionais
1. Implementar S&OP sazonal com gatilhos mensais e pré-build de stock antes do pico.
2. Definir governança de pricing por país para peak season (faixas de desconto, guardrails de margem).
3. Rever mix de produtos por mercado no pico para proteger margem sem perder volume.
4. Reforçar planeamento logístico para novembro-dezembro (capacidade, lead times, contingência).
5. Criar dashboard executivo mensal com `Seasonality Index`, `Avg Ticket`, `Gross Margin` por região/país/categoria.

## 7. Pressupostos e limitações
- Agregação sobre todos os anos (2020-2025) pode ocultar alterações estruturais anuais.
- `Country` nulo removido apenas em S-A2; `Main_Category` nulo removido apenas em S-A3/S-A4.
- Definição de S-A2: `Peak = [11,12,1,2,3]`, `Low = [5,6,7,8,9]`.
- Margem agregada calculada por quociente de somas (correto para decisão).
- Limitação relevante: este eixo não inclui custos de transporte/expedição, logo a explicação causal completa da margem fica parcial.

## 8. O que deve ir para slide
**Visuais mais fortes:**
1. `sa1_region_seasonality_heatmap.png`
2. `sa4_heatmap_month_main_category_seasonality_index.png`
3. `sa2_top_revenue_avg_ticket_peak_vs_low.png`

**Mensagem de apoio (apêndice):**
- `sa3_avg_production_cost_by_month_category.png` para sustentar que custo de produção não dispara no pico.

## 9. 5 bullets finais prontos para apresentação
- A sazonalidade da SkiWell é clara e previsível: dezembro concentra o pico de volume e revenue.
- O padrão é consistente entre regiões e categorias, com vales em maio/junho.
- Em vários países o ticket sobe no pico, mas a margem não melhora na mesma proporção.
- A erosão de margem em mercados específicos indica problema de execução comercial, não só de procura.
- O custo de produção não mostra subida forte na peak season; foco deve ir para pricing, mix, inventário e logística.

## 10. 3 títulos executivos possíveis para o slide
1. **Pico de Procura Não Garante Pico de Margem**
2. **Sazonalidade Forte da SkiWell: Onde a Rentabilidade Escapa no Pico**
3. **Dezembro É Previsível; A Margem, Nem Sempre**
