import sqlite3
import pandas as pd

def verificar_banco():
    conn = sqlite3.connect('nutrition.db')
    cursor = conn.cursor()
    
    # Total de registros
    cursor.execute('SELECT COUNT(*) FROM alimentos')
    total = cursor.fetchone()[0]
    
    # Registros traduzidos
    cursor.execute('SELECT COUNT(*) FROM alimentos WHERE traduzido = 1')
    traduzidos = cursor.fetchone()[0]
    
    # Registros não traduzidos
    cursor.execute('SELECT COUNT(*) FROM alimentos WHERE traduzido = 0')
    nao_traduzidos = cursor.fetchone()[0]
    
    print(f"\nEstatísticas do Banco de Dados:")
    print(f"Total de registros: {total}")
    print(f"Registros traduzidos: {traduzidos}")
    print(f"Registros não traduzidos: {nao_traduzidos}")
    
    # Amostra de registros traduzidos
    print("\nAmostra de 5 registros traduzidos:")
    cursor.execute('''
    SELECT nome_en, nome_pt 
    FROM alimentos 
    WHERE traduzido = 1 
    LIMIT 5
    ''')
    for row in cursor.fetchall():
        print(f"{row[0]} -> {row[1]}")
    
    # Amostra de registros não traduzidos
    print("\nAmostra de 5 registros não traduzidos:")
    cursor.execute('''
    SELECT nome_en 
    FROM alimentos 
    WHERE traduzido = 0 
    LIMIT 5
    ''')
    for row in cursor.fetchall():
        print(row[0])
    
    conn.close()

if __name__ == "__main__":
    verificar_banco() 