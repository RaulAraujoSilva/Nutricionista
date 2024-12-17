import sqlite3
import pandas as pd

def verificar_banco():
    conn = sqlite3.connect('nutrition.db')
    cursor = conn.cursor()
    
    # Estatísticas gerais
    cursor.execute('SELECT COUNT(*) FROM alimentos')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM alimentos WHERE traduzido = 1')
    traduzidos = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM alimentos WHERE traduzido = 0')
    nao_traduzidos = cursor.fetchone()[0]
    
    print("\nEstatísticas do Banco de Dados:")
    print(f"Total de registros: {total}")
    print(f"Registros traduzidos: {traduzidos} ({(traduzidos/total*100):.1f}%)")
    print(f"Registros não traduzidos: {nao_traduzidos} ({(nao_traduzidos/total*100):.1f}%)")
    
    # Amostra de diferentes categorias
    print("\nAmostra de 5 traduções do início do banco:")
    cursor.execute('''
    SELECT nome_en, nome_pt 
    FROM alimentos 
    WHERE traduzido = 1 
    LIMIT 5
    ''')
    for row in cursor.fetchall():
        print(f"{row[0]} -> {row[1]}")
    
    print("\nAmostra de 5 traduções do meio do banco:")
    cursor.execute('''
    SELECT nome_en, nome_pt 
    FROM alimentos 
    WHERE traduzido = 1 
    LIMIT 5 OFFSET ?
    ''', (total // 2,))
    for row in cursor.fetchall():
        print(f"{row[0]} -> {row[1]}")
    
    print("\nAmostra de 5 traduções do final do banco:")
    cursor.execute('''
    SELECT nome_en, nome_pt 
    FROM alimentos 
    WHERE traduzido = 1 
    ORDER BY id DESC
    LIMIT 5
    ''')
    for row in cursor.fetchall():
        print(f"{row[0]} -> {row[1]}")
    
    # Verifica registros não traduzidos (se houver)
    if nao_traduzidos > 0:
        print("\nAmostra de registros não traduzidos:")
        cursor.execute('''
        SELECT nome_en 
        FROM alimentos 
        WHERE traduzido = 0 
        LIMIT 5
        ''')
        for row in cursor.fetchall():
            print(row[0])
    
    # Verifica possíveis problemas
    print("\nVerificando possíveis problemas:")
    
    # Registros com tradução igual ao original
    cursor.execute('''
    SELECT COUNT(*) 
    FROM alimentos 
    WHERE LOWER(nome_en) = LOWER(nome_pt) 
    AND traduzido = 1
    ''')
    iguais = cursor.fetchone()[0]
    if iguais > 0:
        print(f"- {iguais} registros têm tradução igual ao original")
    
    # Registros com tradução vazia
    cursor.execute('''
    SELECT COUNT(*) 
    FROM alimentos 
    WHERE nome_pt IS NULL OR trim(nome_pt) = ""
    ''')
    vazios = cursor.fetchone()[0]
    if vazios > 0:
        print(f"- {vazios} registros têm tradução vazia")
    
    conn.close()

if __name__ == "__main__":
    verificar_banco() 