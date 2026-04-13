import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Carregar os dados
df = pd.read_csv('data/sales_data_clean.csv')
df['GP'] = df['Sales_Price'] - df['Production_Cost']
df['Gross_Margin'] = df['GP'] / df['Sales_Price'] * 100

# 2. Calcular Agregações por País e Ano
# Vamos calcular o Preço Médio, Custo de Produção Médio e a Margem Bruta Média
analise_pais_ano = df.groupby(['Country', 'Year']).agg(
    Avg_Sales_Price=('Sales_Price', 'mean'),
    Avg_Production_Cost=('Production_Cost', 'mean'),
    Avg_Gross_Margin=('Gross_Margin', 'mean'),
    Volume=('Sales_Order_ID', 'count')
).reset_index()

# 3. Mostrar a Tabela Dinâmica (Pivot Table) do Preço Médio por Ano e País
pivot_price = analise_pais_ano.pivot(index='Country', columns='Year', values='Avg_Sales_Price')
print("=== Evolução do Preço Médio de Venda (€) por País (2020 - 2025) ===")
print(pivot_price.round(2))
print("\n")

# Mostrar a evolução da Margem Bruta
pivot_margin = analise_pais_ano.pivot(index='Country', columns='Year', values='Avg_Gross_Margin')
print("=== Evolução da Margem Bruta Média (%) por País (2020 - 2025) ===")
print(pivot_margin.round(2))
print("\n")

# 4. Gerar Visualização: Evolução do Preço Médio de Venda por País
plt.figure(figsize=(14, 8))
sns.lineplot(data=analise_pais_ano, x='Year', y='Avg_Sales_Price', hue='Country', marker='o', linewidth=2)

plt.title('Evolução do Preço Médio de Venda por País (2020-2025)', fontsize=16, fontweight='bold')
plt.xlabel('Ano', fontsize=12)
plt.ylabel('Preço Médio de Venda (€)', fontsize=12)
plt.legend(title='País', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# Salvar o gráfico
caminho_grafico = 'Produto/evolucao_preco_pais_ano.png'
plt.savefig(caminho_grafico)
print(f"Gráfico guardado com sucesso em: {caminho_grafico}")

# 5. Gerar Visualização: Preço vs Custo Geral (Global)
global_ano = df.groupby('Year').agg(
    Avg_Sales_Price=('Sales_Price', 'mean'),
    Avg_Production_Cost=('Production_Cost', 'mean')
).reset_index()

plt.figure(figsize=(10, 6))
plt.plot(global_ano['Year'], global_ano['Avg_Sales_Price'], marker='o', linewidth=2, label='Preço Médio de Venda', color='blue')
plt.plot(global_ano['Year'], global_ano['Avg_Production_Cost'], marker='s', linewidth=2, label='Custo Médio de Produção', color='red')
plt.fill_between(global_ano['Year'], global_ano['Avg_Sales_Price'], global_ano['Avg_Production_Cost'], color='blue', alpha=0.1)

plt.title('Global: Evolução do Preço Médio vs Custo Médio de Produção (2020-2025)', fontsize=14, fontweight='bold')
plt.xlabel('Ano', fontsize=12)
plt.ylabel('Valor (€)', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

caminho_grafico_global = 'Produto/evolucao_preco_vs_custo_global.png'
plt.savefig(caminho_grafico_global)
print(f"Gráfico guardado com sucesso em: {caminho_grafico_global}")
