import pandas as pd
import sqlite3
import openai
import time
from typing import List

# Configuração da API OpenAI
openai.api_key = "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"
openai.organization = "org-qWlrlvk9nDmo3OglC0VwZQxo"

def criar_banco():
    """Cria o banco de dados e a tabela"""
    conn = sqlite3.connect('nutrition.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_en TEXT NOT NULL,
        nome_pt TEXT,
        traduzido INTEGER DEFAULT 0
    )
    ''')
    
    conn.commit()
    return conn

def carregar_dados(conn, csv_file):
    """Carrega dados do CSV"""
    df = pd.read_csv(csv_file, encoding='latin1')
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        cursor.execute('INSERT INTO alimentos (nome_en) VALUES (?)', (row['FoodName'],))
    
    conn.commit()
    print(f"Carregados {len(df)} registros")

def traduzir_lote(items: List[str]) -> List[str]:
    """Traduz um lote de itens"""
    prompt = """Traduza os seguintes alimentos para português brasileiro.
Regras:
1. Retorne APENAS as traduções, uma por linha
2. Mantenha nomes próprios (ex: Bonox -> Bonox)
3. Traduza TODOS os termos possíveis
4. Mantenha o formato do texto original

Alimentos:
"""
    prompt += "\n".join(items)
    
    try:
        client = openai.OpenAI(
            api_key=openai.api_key,
            organization=openai.organization
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um tradutor especializado em nomes de alimentos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip().split('\n')
    except Exception as e:
        print(f"Erro: {e}")
        return items

def processar_traducoes():
    """Processa todas as traduções"""
    conn = criar_banco()
    
    # Carrega dados
    print("Carregando dados...")
    carregar_dados(conn, 'Data/Nutrition Dataset.csv')
    
    cursor = conn.cursor()
    tamanho_lote = 5
    
    # Conta total de registros
    cursor.execute('SELECT COUNT(*) FROM alimentos WHERE traduzido = 0')
    total = cursor.fetchone()[0]
    
    print(f"\nIniciando tradução de {total} registros...")
    traduzidos = 0
    
    while True:
        # Pega próximo lote
        cursor.execute('''
        SELECT id, nome_en 
        FROM alimentos 
        WHERE traduzido = 0 
        LIMIT ?
        ''', (tamanho_lote,))
        
        registros = cursor.fetchall()
        if not registros:
            break
        
        # Prepara e traduz
        ids = [r[0] for r in registros]
        nomes = [r[1] for r in registros]
        traducoes = traduzir_lote(nomes)
        
        # Atualiza banco
        for id_reg, nome_en, nome_pt in zip(ids, nomes, traducoes):
            cursor.execute('''
            UPDATE alimentos 
            SET nome_pt = ?, traduzido = 1 
            WHERE id = ?
            ''', (nome_pt, id_reg))
            
            print(f"{nome_en} -> {nome_pt}")
        
        conn.commit()
        traduzidos += len(registros)
        print(f"Progresso: {traduzidos}/{total} ({(traduzidos/total*100):.1f}%)")
        print("-" * 40)
        
        time.sleep(2)
    
    # Exporta resultados
    df = pd.read_sql_query('''
    SELECT nome_en as "Nome Original", 
           nome_pt as "Nome Traduzido"
    FROM alimentos
    ''', conn)
    
    df.to_csv('traducoes_final.csv', index=False, encoding='utf-8')
    print("\nTraduções exportadas para traducoes_final.csv")
    
    conn.close()

if __name__ == "__main__":
    processar_traducoes() 