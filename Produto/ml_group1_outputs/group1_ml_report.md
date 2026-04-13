# Group 1 ML Insight System

## Objetivo
Criar um sistema de ML para apoiar o Grupo 1 do enunciado:
- diagnosticar a performance das geografias;
- identificar constrangimentos relevantes;
- transformar o diagnostico em watchlists e insights acionaveis.

## Algoritmos usados
- Random Forest Regressor para estimar `profit_margin_pct`
- Random Forest Regressor para estimar `shipping_ratio`
- KMeans para descobrir arquetipos de segmentos
- Isolation Forest para detetar segmentos anormais

## Performance dos modelos
- Modelo estrutural de margem: R2 0.297 | RMSE 0.0147 | MAE 0.0114
- Modelo de shipping: R2 0.921 | RMSE 0.0029 | MAE 0.0022

## Drivers mais relevantes
- Drivers do modelo estrutural de margem: has_shipping_rate, avg_delivery_days, Subcategory, avg_shop_age, Country
- Drivers do modelo de shipping: has_shipping_rate, avg_delivery_days, Subcategory, orders_yoy_growth, avg_sales_price

## Principais sinais encontrados
- Geografia mais critica no watchlist: China (Asia) com risk score medio de 51.2, margem media de 0.394 e shipping ratio medio de 0.054.
- Geografia mais robusta no watchlist: Japan (Asia) com risk score medio de 37.4.
- O cluster com maior peso de receita e "Core rentavel" e representa 47.0% da receita dos segmentos analisados.
- O cluster mais arriscado e "Pressao logistica" com risk score medio de 48.2.
- A maior concentracao de anomalias esta em China (Asia), com 109 segmentos anormais, ou 37.2% do total.
- O numero de clusters escolhido pelo sistema foi 3.

## Anomalias prioritarias
- China | 2020 Q2 | Neck warmers | risk 84.3 | margem baixa, abaixo do esperado pelo modelo, pressao de shipping
- China | 2021 Q3 | Jackets | risk 83.7 | margem baixa, abaixo do esperado pelo modelo, pressao de shipping
- China | 2020 Q4 | Ski socks | risk 80.6 | margem baixa, abaixo do esperado pelo modelo, pressao de shipping
- China | 2020 Q3 | Goggles | risk 79.9 | margem baixa, abaixo do esperado pelo modelo, pressao de shipping
- China | 2021 Q1 | Hats | risk 78.8 | margem baixa, abaixo do esperado pelo modelo, pressao de shipping

## Como usar na apresentacao
- Usar o watchlist por pais para sustentar a parte de diagnostico geografico.
- Usar os drivers do modelo para separar causas estruturais (produto/geografia) de causas operacionais (shipping e concentracao).
- Usar clusters e anomalias para mostrar onde estao os segmentos que fogem ao padrao esperado e exigem acao.

## Ficheiros gerados
- `margin_model_feature_importance.csv`
- `shipping_model_feature_importance.csv`
- `segment_ml_scores.csv`
- `segment_cluster_profiles.csv`
- `segment_anomalies.csv`
- `country_anomaly_summary.csv`
- `country_watchlist.csv`
- `geography_year_watchlist.csv`
- `group1_geography_risk_heatmap.png`
- `group1_segment_clusters.png`
