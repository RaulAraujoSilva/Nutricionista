import sqlite3
import pandas as pd

def exportar_banco():
    # Conecta ao banco
    conn = sqlite3.connect('nutrition.db')
    
    # Lê o arquivo CSV original para pegar todas as colunas
    df_original = pd.read_csv('Data/Nutrition Dataset.csv', encoding='latin1')
    
    # Lê as traduções do banco
    df_traducoes = pd.read_sql_query('''
    SELECT 
        a.id,
        a.nome_en as "Nome Original",
        a.nome_pt as "Nome em Português",
        a.traduzido as "Tradução Concluída"
    FROM alimentos a
    ''', conn)
    
    # Merge dos dados originais com as traduções
    df_final = pd.merge(
        df_original,
        df_traducoes,
        left_on='FoodName',
        right_on='Nome Original',
        how='left'
    )
    
    # Remove a coluna duplicada
    df_final = df_final.drop('Nome Original', axis=1)
    
    # Salva o arquivo final
    arquivo_saida = 'banco_nutricional_completo.csv'
    df_final.to_csv(arquivo_saida, sep=';', index=False, encoding='utf-8-sig')
    
    print(f"\nDados exportados para {arquivo_saida}")
    print(f"Total de registros: {len(df_final)}")
    print(f"Total de colunas: {len(df_final.columns)}")
    print("\nPrimeiras 5 colunas:")
    for col in list(df_final.columns)[:5]:
        print(f"- {col}")

if __name__ == "__main__":
    exportar_banco() 