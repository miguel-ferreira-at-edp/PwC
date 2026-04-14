# Auditoria Final do Repositorio - SkiWell Sports

## 1. Resumo executivo geral
A leitura do repositorio mostra maturidade elevada nos eixos **Financeiro**, **Produto** e **Sazonalidade**, com resultados suficientes para narrativa executiva. O eixo **Logistica** tem boa profundidade analitica no notebook, mas com lacunas de rastreabilidade (artefactos nao exportados fora do `.ipynb`) e uma fragilidade metodologica relevante em agregacoes de margem/ratio por media simples.

Em termos de alinhamento com as notas, o quadro geral e:
- **Globalmente alinhado**, sobretudo em sazonalidade e parte de produto.
- **Parcialmente alinhado** em varios pontos financeiros (ex.: pico absoluto nao e 2022; crescimento regional nao liderado pela Asia).
- **Nao alinhado** em algumas afirmacoes quantitativas especificas (ex.: "755 produtos com margem <20%" nao e suportado na base atual).

## 2. Metodologia de leitura do repositorio
- Mapeamento inicial de pastas e ficheiros por eixo.
- Leitura do plano base em `Lobão/Dados/Grupo 1/Plano de Implementacao/skiwell_plano_analise_v2.docx` para identificar analises previstas (F-A*, P-A*, S-A*, L-A*).
- Priorizacao de evidencia em outputs existentes (`.csv`, `.png`, `.md`, notebooks e scripts).
- Validacao quantitativa complementar em `data/sales_data_clean.csv` e `Lobão/Dados/sales_data_sazonalidade_work.csv` apenas para conferir coerencia de conclusoes ja produzidas.

## 3. Mapeamento do repositorio por eixo
- **Financeiro**: `Financeiro/global`, `Financeiro/continentes`, `Financeiro/paises`, `Financeiro/lojas`, `Financeiro/lojas_tipo`.
- **Produto**: `Produto/analise_produto.ipynb`, scripts `Produto/analise_preco_pais_ano.py`, `Produto/analise_variacao_preco.py`, outputs `Produto/*.png`, `Produto/price_variation_analysis.csv`, `Produto/ml_group1_outputs/*`.
- **Sazonalidade**: `Lobão/Dados/sa1_outputs`, `sa2_outputs`, `sa3_outputs`, `sa4_outputs`, relatorios markdown de consolidacao.
- **Logistica**: `Logistica/logistics.ipynb` (analise completa no notebook), sem pasta dedicada de outputs exportados em separado.

## 4. Eixo Financeiro
### A. O que estava previsto no plano
Previstas analises F-A1 a F-C3, cobrindo evolucao global, diferencas por regiao/pais, dimensao de loja e leitura de risco para decisao.

### B. O que existe no repositorio
- Scripts e graficos extensos por nivel:
  - Global: `Financeiro/global/revenue_global.py`, `gross_profit_global.py`, `gross_margin_global.py`, `net_margin_global.py`, `ticket_medio_global.py`, etc.
  - Regioes/paises: `Financeiro/continentes/*`, `Financeiro/paises/*`.
  - Lojas e tipo de loja: `Financeiro/lojas/revenue_gross_profit_lojas.py`, `Financeiro/lojas_tipo/revenue_gross_profit_lojas_tipo.py`.
- Numerosos `.png` de tendencias e tabelas de estatistica.

### C. O que os resultados mostram
Com base nos outputs e validacao da base `data/sales_data_clean.csv`:
- Revenue e gross profit crescem com trajetorias muito proximas em YoY.
- Pico absoluto de revenue/gross profit ocorre em 2025; 2022 e o maior salto YoY.
- Gross margin e net margin mantem-se muito estaveis ao longo dos anos.
- Crescimento 2020->2025 por regiao: North America > Europe > Asia.
- Por pais, China e o maior crescimento e ganha share; South Korea perde share e entra em queda apos 2022.

### D. Validacao das notas
Detalhe completo na matriz: `repo_auditoria_skiwell_matriz_validacao_notas.md`.
Resumo: parte importante das notas e confirmada (estabilidade de margem, ganho relativo da China), mas ha correcoes necessarias em crescimento regional e no "pico em 2022".

### E. Conclusao do eixo
Eixo forte para storytelling de performance, com boa cobertura multi-granular. Principal lacuna: nao ha artefacto explicito de score composto Red/Amber/Green (F-B4) e leitura de decisao integrada diretamente no eixo financeiro.

## 5. Eixo Produto
### A. O que estava previsto no plano
Previstas analises P-A1, P-A2, P-A3, P-B1, P-B2 e KPIs P01-P06 (margem, custo, share, variacao de preco, concentracao).

### B. O que existe no repositorio
- Notebook central: `Produto/analise_produto.ipynb` com as secoes P-A1 a P-B2.
- Outputs visuais amplos: `Produto/PA1_*`, `PA2_*`, `PA3_*`, `PB1_*`, `PB2_*`, `pareto_produtos.png`, etc.
- Ficheiros complementares: `Produto/price_variation_analysis.csv`, `Produto/ml_group1_outputs/group1_ml_report.md`.

### C. O que os resultados mostram
- Share por categoria global relativamente estavel.
- Forte relacao entre preco e custo (consistente com regra de pricing por base de custo, sem provar causalidade).
- Existem produtos com dispersao de preco muito elevada por pais (P-B1).
- Pareto reportado no notebook: ~1208 produtos concentram 80% da receita.
- No notebook: 0 subcategorias com gross margin <20% (P-A2).
- Analise de cor feita por extração textual de `Product_Name` com cobertura parcial (~85.8%).

### D. Validacao das notas
Resumo: varias notas estao confirmadas (dispersao de preco, pareto, salto de volume na Asia 2022), mas ha hipoteses nao suportadas ou parciais (uniformidade por cor/tamanho por regiao/pais e "755 produtos <20% margem").

### E. Conclusao do eixo
Eixo bem desenvolvido e rico visualmente. Ponto de atencao metodologico: em varias agregacoes do notebook, `Margin_pct` e calculada por media de margem linha-a-linha; para decisao executiva, convem priorizar margem agregada ponderada por receita.

## 6. Eixo Sazonalidade
### A. O que estava previsto no plano
Previstas S-A1, S-A2, S-A3 e S-A4, focadas em padrao mensal de procura, preco medio por pais, custo de producao e sazonalidade por categoria.

### B. O que existe no repositorio
Cobertura completa com artefactos dedicados:
- `Lobão/Dados/sa1_outputs/*`
- `Lobão/Dados/sa2_outputs/*`
- `Lobão/Dados/sa3_outputs/*`
- `Lobão/Dados/sa4_outputs/*`
- Relatorios: `Lobão/Dados/relatorio_final_eixo_sazonalidade.md`, `resumo_executivo_eixo_sazonalidade.md`.

### C. O que os resultados mostram
- Pico global de revenue em dezembro; vale em maio/junho.
- Indice sazonal por regiao e categoria confirma sincronizacao do pico de fim de ano.
- Em S-A2, ticket sobe em varios paises, mas a margem nao melhora de forma uniforme (ha deltas negativos em alguns mercados).
- Em S-A3, desvios de custo de producao existem, mas nao apontam subida forte e generalizada no pico sazonal de vendas.

### D. Validacao das notas
Este e o eixo mais alinhado com as notas. As mensagens centrais de sazonalidade estao largamente confirmadas.

### E. Conclusao do eixo
Eixo robusto, coerente e pronto para apresentacao. A narrativa operacional (pre-build de stock, ajuste de pricing/mix por mercado e coordenação com logistica) esta bem suportada.

## 7. Eixo Logistica
### A. O que estava previsto no plano
Previstas L-A1 a L-A5 com subset de pedidos com shipping, cobrindo transportadora x pais, impacto em margem, custo por categoria, consolidacao e custo x lead-time.

### B. O que existe no repositorio
- Notebook completo: `Logistica/logistics.ipynb` com outputs executados no proprio ficheiro.
- Evidencia explicita no notebook de L-A1..L-A5 e KPIs L01..L07.

### C. O que os resultados mostram
Pelo notebook:
- Subset shipping: 26.480 linhas (~18% do total).
- L01 total shipping ~EUR 532.545; L02 avg ~EUR 20.11; ratio medio ~10%.
- Technical equipment com maior shipping medio (L-A3).
- Potencial de consolidacao elevado com janela <5 dias (L-A4/L07), incluindo estimativa de poupanca relevante.
- Quadrantes de custo/lead-time por transportadora x pais (L-A5).

### D. Validacao das notas
Notas logisticas estao maioritariamente confirmadas ou parciais. O racional de consolidacao esta suportado de forma clara.

### E. Conclusao do eixo
Analise rica, mas com duas fragilidades:
- Artefactos externos (CSV/PNG) nao estao visiveis fora do notebook.
- Funcao agregadora no notebook usa medias simples para alguns ratios/margens (`mean`), o que pode distorcer leitura executiva quando ha heterogeneidade de receita.

## 8. Matriz de validacao das notas
A matriz detalhada (linha a linha) esta em:
- `repo_auditoria_skiwell_matriz_validacao_notas.md`

Resumo de estado:
- **CONFIRMADO**: 18
- **PARCIALMENTE SUPORTADO**: 13
- **NAO SUPORTADO**: 5
- **EM FALTA**: 1

## 9. Principais resultados realmente suportados
1. Sazonalidade de procura forte e previsivel com pico em dezembro e baixa em maio/junho.
2. Efeito sazonal de preco/ticket e mais forte que o efeito sazonal em margem.
3. Ha paises em que a margem piora no pico, apesar de maior ticket.
4. Revenue e gross profit evoluem de forma muito alinhada no tempo.
5. Margens (gross e net) estao estruturalmente estaveis.
6. China e o pais com maior crescimento e ganho de share.
7. South Korea perde share e apresenta queda apos 2022.
8. Technical equipment tem maior custo logistico medio.
9. Consolidacao de encomendas (<5 dias) mostra potencial economico relevante no eixo logistico.
10. Pareto de portfolio e concentrado (~1208 produtos para 80% da receita no output de produto).

## 10. Principais pontos fracos / analises incompletas
1. Ausencia de score composto Red/Amber/Green claramente materializado no eixo financeiro (F-B4).
2. Framework de decisao de encerramento por geografia nao esta consolidado num artefacto unico no repositorio.
3. No eixo logistico, outputs estao sobretudo embebidos no `.ipynb` (rastreabilidade mais fraca).
4. No notebook logistico, margens/ratios agregados por media simples em partes criticas.
5. Hipotese "755 produtos com margem <20%" nao e suportada na base atual.
6. Uniformidade por cor/tamanho por regiao/pais nao esta demonstrada com evidencia forte (tamanho em falta).
7. Algumas mensagens financeiras (pico em 2022; Asia lidera crescimento regional) precisam de correcao quantitativa.
8. Nota de "production cost fixo" nao e suportada em nivel absoluto.
9. Eixo produto tem elevada densidade visual, mas sem uma tabela final unica de priorizacao executiva.
10. Ha relatorios antigos de sazonalidade com estado historico diferente (quando `sa1_outputs` estava ausente), exigindo cuidado de versao.

## 11. O que ja esta pronto para apresentacao
- Narrativa de sazonalidade completa (S-A1..S-A4) com CSV/PNG dedicados.
- Narrativa financeira de evolucao e diferencas geograficas com muitos visuais.
- Narrativa de produto com pareto, variacao de preco por pais e leitura de risco por subcategoria.
- Narrativa logistica forte no conteudo analitico do notebook (com ressalvas de forma).

## 12. O que ainda precisa de validacao
1. Consolidar formalmente o score de decisao (pais Red/Amber/Green) num output unico.
2. Recalcular/confirmar margens agregadas ponderadas em partes do eixo produto e logistico onde ha media simples.
3. Definir se a equipa vai manter analise de cor/tamanho como insight auxiliar ou remover por baixa robustez.
4. Extrair do notebook logistico uma pasta de outputs versionaveis (CSV/PNG) para auditoria final.

## 13. Recomendacoes para a equipa sobre como contar a historia final
- Abrir com "o que mudou na rentabilidade e onde" (financeiro).
- Mostrar concentracao de valor e variabilidade de pricing (produto).
- Explicar previsibilidade da procura e gargalo de conversao em margem (sazonalidade).
- Fechar com alavancas operacionais concretas e score por geografia (logistica + decisao).

### 13.1 Dez conclusoes mais fortes
1. A sazonalidade da SkiWell e estrutural e previsivel.
2. Dezembro e pico consistente em multiplas visoes.
3. Maio/junho concentra vale de procura.
4. Ticket sazonal sobe, margem nao necessariamente.
5. A heterogeneidade por pais e real e material.
6. Custo de producao sozinho nao explica margem sazonal.
7. China acelera e ganha relevancia no mix geografico.
8. South Korea fragiliza no periodo recente.
9. Custos logisticos por categoria diferem fortemente (technical equipment mais caro).
10. Ha espaco relevante para poupanca via consolidacao logistica.

### 13.2 Dez conclusoes fracas ou nao totalmente suportadas
1. "Pico financeiro em 2022" (nao em valor absoluto).
2. "Asia e a regiao com maior crescimento percentual".
3. "Production cost fixo" (absoluto).
4. "Ticket medio completamente fixo".
5. "755 produtos com margem <20%".
6. "10% dos produtos <20% margem e 1% da receita".
7. "Distribuicao de cores uniforme por regiao/pais".
8. "Distribuicao de tamanhos uniforme por regiao/pais".
9. "Coreia estagnada" sem qualificar queda pos-2022.
10. Inferencias causais fortes de pricing apenas por correlacao preco-custo.

### 13.3 Cinco sugestoes de melhoria imediata
1. Criar `score_geografico_final.csv` com regra explicita Red/Amber/Green.
2. Normalizar formula de margem agregada para `sum(GP)/sum(Revenue)` em todos os eixos.
3. Exportar outputs do eixo logistico para pasta dedicada (`csv/png`) fora do notebook.
4. Produzir um "one-pager" de metodologia comum (exclusoes, formulas, definicoes de temporada).
5. Criar slide final de priorizacao impacto x esforco por geografia/alavanca.
