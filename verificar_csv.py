import pandas as pd

def verificar_csv():
    # Lê o arquivo CSV
    df = pd.read_csv('banco_nutricional_completo.csv', sep=';', encoding='utf-8-sig')
    
    print("\nInformações do arquivo exportado:")
    print(f"Total de registros: {len(df)}")
    print(f"Total de colunas: {len(df.columns)}")
    
    print("\nColunas disponíveis:")
    for col in df.columns:
        print(f"- {col}")
    
    print("\nAmostra de 5 registros (apenas colunas relevantes):")
    amostra = df[['FoodName', 'Nome em Português', 'Tradução Concluída']].head()
    print(amostra.to_string())

if __name__ == "__main__":
    verificar_csv() 