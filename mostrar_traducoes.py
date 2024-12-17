import sqlite3

def mostrar_traducoes():
    conn = sqlite3.connect('nutrition.db')
    cursor = conn.cursor()
    
    print("\nAmostra de 10 registros completos:")
    print("-" * 100)
    print(f"{'ID':<6} | {'Nome Original':<40} | {'Nome Traduzido':<40} | {'Traduzido'}")
    print("-" * 100)
    
    cursor.execute('''
    SELECT id, nome_en, nome_pt, traduzido 
    FROM alimentos 
    LIMIT 10
    ''')
    
    for row in cursor.fetchall():
        id_reg, nome_en, nome_pt, traduzido = row
        print(f"{id_reg:<6} | {nome_en[:40]:<40} | {nome_pt[:40] if nome_pt else 'Não traduzido':<40} | {traduzido}")
    
    conn.close()

if __name__ == "__main__":
    mostrar_traducoes() 