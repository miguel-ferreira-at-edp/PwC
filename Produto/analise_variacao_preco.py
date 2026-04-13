
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Carregamento
df = pd.read_csv('data/sales_data_clean.csv', parse_dates=['Order_Date'])
df['YearMonth'] = df['Order_Date'].dt.to_period('M').astype(str)

# 1. Variação por Produto e País (Visão Geral)
price_variation = df.groupby(['Product_ID', 'Product_Name', 'Country']).agg(
    avg_price=('Sales_Price', 'mean'),
    std_price=('Sales_Price', 'std'),
    min_price=('Sales_Price', 'min'),
    max_price=('Sales_Price', 'max'),
    count=('Sales_Price', 'count')
).reset_index()

price_variation['CV'] = (price_variation['std_price'] / price_variation['avg_price']) * 100

print("=== Produtos com maior variação de preço (CV) por País ===")
print(price_variation.sort_values('CV', ascending=False).head(10)[['Product_Name', 'Country', 'avg_price', 'CV']])

# 2. Variação Temporal (Médias mensais por Produto e País)
temporal_variation = df.groupby(['Product_ID', 'Country', 'YearMonth']).agg(
    monthly_avg_price=('Sales_Price', 'mean')
).reset_index()

# Calcular a variação temporal (CV temporal por produto-país)
temporal_cv = temporal_variation.groupby(['Product_ID', 'Country']).agg(
    temporal_avg=('monthly_avg_price', 'mean'),
    temporal_std=('monthly_avg_price', 'std')
).reset_index()
temporal_cv['Temporal_CV'] = (temporal_cv['temporal_std'] / temporal_cv['temporal_avg']) * 100

print("\n=== Produtos com maior variação temporal de preço (Temporal CV) por País ===")
print(temporal_cv.sort_values('Temporal_CV', ascending=False).head(10))

# 3. Comparação de Preços entre Países para o mesmo Produto
cross_country = df.groupby(['Product_ID', 'Product_Name']).agg(
    price_range_pct=('Sales_Price', lambda x: (x.max() - x.min()) / x.mean() * 100),
    n_countries=('Country', 'nunique')
).reset_index()

print("\n=== Produtos com maior discrepância de preço entre países ===")
print(cross_country[cross_country['n_countries'] > 1].sort_values('price_range_pct', ascending=False).head(10))

# 4. Visualização de Casos Críticos
# Selecionar os 5 produtos com maior CV temporal global
top_variable_products = temporal_cv.sort_values('Temporal_CV', ascending=False).head(5)['Product_ID'].unique()

plt.figure(figsize=(15, 10))
for i, pid in enumerate(top_variable_products):
    plt.subplot(3, 2, i+1)
    data_plot = temporal_variation[temporal_variation['Product_ID'] == pid]
    sns.lineplot(data=data_plot, x='YearMonth', y='monthly_avg_price', hue='Country', marker='o')
    plt.title(f'Variação de Preço: {pid}')
    plt.xticks(rotation=45)
    plt.ylabel('Preço Médio Mensal')

plt.tight_layout()
plt.savefig('Produto/variacao_preco_produto_pais_tempo.png')
print("\nVisualização salva em 'Produto/variacao_preco_produto_pais_tempo.png'")
