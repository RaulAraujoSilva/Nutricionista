import pandas as pd
import sqlite3
import openai
import time
import os
from typing import List
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração da API OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.organization = os.getenv('OPENAI_ORGANIZATION')

def criar_banco():
    """Cria o banco de dados e a tabela de alimentos"""
    conn = sqlite3.connect('nutrition.db')
    cursor = conn.cursor()
    
    # Cria a tabela
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
    """Carrega os dados do CSV para o banco"""
    df = pd.read_csv(csv_file, encoding='latin1')
    print("Colunas disponíveis:", df.columns.tolist())
    
    cursor = conn.cursor()
    
    # Insere os dados do CSV
    for _, row in df.iterrows():
        cursor.execute('''
        INSERT INTO alimentos (nome_en) VALUES (?)
        ''', (row['FoodName'],))
    
    conn.commit()
    print(f"Carregados {len(df)} registros no banco de dados")

def traduzir_lote(items: List[str]) -> List[str]:
    """Traduz um lote de itens usando a API do OpenAI"""
    prompt = """Traduza os seguintes alimentos para português brasileiro.
Regras:
1. Retorne APENAS as traduções, uma por linha
2. Mantenha nomes próprios (ex: Bonox -> Bonox)
3. Traduza TODOS os termos possíveis
4. Mantenha o formato do texto original (maiúsculas/minúsculas)
5. Não adicione informações extras

Alimentos para traduzir:
"""
    prompt += "\n".join(items)
    
    try:
        client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            organization=os.getenv('OPENAI_ORGANIZATION')
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um tradutor especializado em nomes de alimentos. Traduza TODOS os termos possíveis para português brasileiro, mantendo apenas nomes próprios em inglês."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        traducoes = response.choices[0].message.content.strip().split('\n')
        
        # Verifica se o número de traduções corresponde ao número de itens
        if len(traducoes) != len(items):
            print(f"Erro: Número de traduções ({len(traducoes)}) diferente do número de itens ({len(items)})")
            return items
            
        # Verifica se alguma tradução está vazia
        if any(not t.strip() for t in traducoes):
            print("Erro: Encontrada tradução vazia")
            return items
        
        return traducoes
        
    except Exception as e:
        print(f"Erro na tradução: {e}")
        return items

def traduzir_todos(conn, tamanho_lote: int = 10):
    """Traduz todos os registros não traduzidos"""
    cursor = conn.cursor()
    
    # Conta total de registros não traduzidos
    cursor.execute('SELECT COUNT(*) FROM alimentos WHERE traduzido = 0')
    total = cursor.fetchone()[0]
    
    if total == 0:
        print("Não há registros para traduzir")
        return
        
    traduzidos = 0
    erros = 0
    ultimo_total = total  # Para verificar se está realmente progredindo
    
    print(f"\nIniciando tradução de {total} registros...")
    
    while True:
        # Verifica novamente o total de não traduzidos
        cursor.execute('SELECT COUNT(*) FROM alimentos WHERE traduzido = 0')
        total_atual = cursor.fetchone()[0]
        
        # Se não houver mais registros para traduzir, para
        if total_atual == 0:
            break
            
        # Se o total não diminuiu após várias tentativas, há um problema
        if total_atual >= ultimo_total and traduzidos > 0:
            print("Aviso: Não há progresso na tradução. Verificando possível loop...")
            break
            
        ultimo_total = total_atual
        
        # Pega o próximo lote de itens não traduzidos
        cursor.execute('''
        SELECT id, nome_en FROM alimentos 
        WHERE traduzido = 0 
        LIMIT ?
        ''', (tamanho_lote,))
        
        registros = cursor.fetchall()
        if not registros:
            break
            
        # Prepara os itens para tradução
        ids = [r[0] for r in registros]
        nomes = [r[1] for r in registros]
        
        try:
            # Traduz os nomes
            traducoes = traduzir_lote(nomes)
            
            # Atualiza o banco com as traduções
            for id_reg, traducao in zip(ids, traducoes):
                cursor.execute('''
                UPDATE alimentos 
                SET nome_pt = ?, traduzido = 1 
                WHERE id = ?
                ''', (traducao, id_reg))
            
            conn.commit()
            traduzidos += len(registros)
            
            # Mostra progresso
            print(f"Progresso: {traduzidos}/{total} ({(traduzidos/total*100):.1f}%)")
            print("Últimas traduções:")
            for nome_en, nome_pt in zip(nomes, traducoes):
                print(f"{nome_en} -> {nome_pt}")
            print("-" * 40)
            
        except Exception as e:
            print(f"Erro ao processar lote: {e}")
            erros += 1
            if erros > 5:  # Limite de erros consecutivos
                print("Muitos erros consecutivos. Parando...")
                break
            time.sleep(5)  # Espera um pouco mais após erro
            continue
            
        # Espera entre as requisições para evitar limites de taxa
        time.sleep(2)
    
    print(f"\nProcesso concluído!")
    print(f"Total traduzido: {traduzidos}")
    print(f"Erros encontrados: {erros}")

def exportar_csv(conn, arquivo_saida: str):
    """Exporta os resultados para um arquivo CSV"""
    df = pd.read_sql_query('''
    SELECT nome_en as "Nome Original", 
           nome_pt as "Nome Traduzido",
           traduzido as "Tradução Concluída"
    FROM alimentos
    ''', conn)
    
    df.to_csv(arquivo_saida, index=False, encoding='utf-8')
    print(f"\nResultados exportados para {arquivo_saida}")

def main():
    # Cria o banco e carrega os dados
    conn = criar_banco()
    
    # Verifica se já existem dados no banco
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM alimentos')
    if cursor.fetchone()[0] == 0:
        carregar_dados(conn, 'Data/Nutrition Dataset.csv')
    
    # Traduz todos os registros
    traduzir_todos(conn)
    
    # Exporta os resultados
    exportar_csv(conn, 'traducoes_alimentos.csv')
    
    conn.close()

if __name__ == "__main__":
    main() 