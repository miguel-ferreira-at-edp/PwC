import pandas as pd
import os 

# Caminho para o dataset
file_path = r'C:\Users\jfran\Documents\PwC\data\sales_data_clean.csv'

def gross_profit():
    if not os.path.exists(file_path):
        print(f"Erro: O ficheiro não foi encontrado em {file_path}")
        return
    print("A carregar os dados...")
    df = pd.read_csv(file_path)
    # Colunas utilizadas para o agrupamento e cálculo
    # 'Main_Category' foi escolhida para representar a Categoria
    columns = ['Year', 'Region', 'Country', 'Main_Category', 'Sales_Price', 'Production_Cost']
    
    # Calcular Gross Profit individual por linha
    df['Gross_Profit'] = df['Sales_Price'] - df['Production_Cost']
    # Agrupar pelos critérios solicitados e somar o Gross Profit
    kpi_result = df.groupby(['Year', 'Region', 'Country', 'Main_Category'])['Gross_Profit'].sum().reset_index()
    # Ordenar para facilitar a leitura
    kpi_result = kpi_result.sort_values(by=['Year', 'Region', 'Country', 'Main_Category'])
    # Guardar os resultados num novo CSV
    output_path = 'gross_profit_kpi_results.csv'
    kpi_result.to_csv(output_path, index=False)
    
    print("\nResumo dos resultados (Top 10):")
    print(kpi_result.head(10).to_string(index=False))
    print(f"\nResultados completos guardados em: {os.path.abspath(output_path)}")
if __name__ == "__main__":
    gross_profit()