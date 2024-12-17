import sqlite3
import openai
import time
from typing import List

# Configuração da API OpenAI
openai.api_key = "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"
openai.organization = "org-qWlrlvk9nDmo3OglC0VwZQxo"

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
            api_key=openai.api_key,
            organization=openai.organization
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
            return None
            
        # Verifica se alguma tradução está vazia
        if any(not t.strip() for t in traducoes):
            print("Erro: Encontrada tradução vazia")
            return None
            
        # Verifica se alguma tradução é igual ao original
        for orig, trad in zip(items, traducoes):
            if orig.lower() == trad.lower():
                print(f"Aviso: Tradução igual ao original: {orig}")
        
        return traducoes
        
    except Exception as e:
        print(f"Erro na tradução: {e}")
        return None

def corrigir_traducoes_existentes(conn):
    """Corrige as traduções já feitas que estão em inglês"""
    cursor = conn.cursor()
    
    # Pega todos os registros marcados como traduzidos
    cursor.execute('''
    SELECT id, nome_en, nome_pt 
    FROM alimentos 
    WHERE traduzido = 1
    ''')
    
    registros = cursor.fetchall()
    total = len(registros)
    print(f"\nVerificando {total} traduções existentes...")
    
    corrigidos = 0
    tamanho_lote = 5
    
    # Processa em lotes
    for i in range(0, total, tamanho_lote):
        lote = registros[i:i+tamanho_lote]
        ids = [r[0] for r in lote]
        nomes = [r[1] for r in lote]
        
        # Se o nome traduzido for igual ao original, retraduz
        traducoes = traduzir_lote(nomes)
        if traducoes is None:
            continue
            
        # Atualiza as traduções
        for id_reg, traducao in zip(ids, traducoes):
            cursor.execute('''
            UPDATE alimentos 
            SET nome_pt = ?, traduzido = 1 
            WHERE id = ?
            ''', (traducao, id_reg))
        
        conn.commit()
        corrigidos += len(lote)
        
        print(f"Progresso: {corrigidos}/{total} ({(corrigidos/total*100):.1f}%)")
        time.sleep(2)
    
    print(f"\nCorreção concluída! {corrigidos} registros processados.")

def continuar_traducao():
    """Continua a tradução dos registros pendentes"""
    conn = sqlite3.connect('nutrition.db')
    cursor = conn.cursor()
    
    # Primeiro corrige as traduções existentes
    print("Iniciando correção das traduções existentes...")
    corrigir_traducoes_existentes(conn)
    
    # Verifica quantos registros faltam traduzir
    cursor.execute('SELECT COUNT(*) FROM alimentos WHERE traduzido = 0')
    total = cursor.fetchone()[0]
    
    if total == 0:
        print("Não há registros pendentes para traduzir")
        conn.close()
        return
    
    print(f"\nContinuando tradução de {total} registros pendentes...")
    
    traduzidos = 0
    erros = 0
    tamanho_lote = 5
    
    while True:
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
            if traducoes is None:
                erros += 1
                if erros > 5:
                    print("Muitos erros consecutivos. Parando...")
                    break
                time.sleep(5)
                continue
            
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
            print(f"\nProgresso: {traduzidos}/{total} ({(traduzidos/total*100):.1f}%)")
            print("Últimas traduções:")
            for nome_en, nome_pt in zip(nomes, traducoes):
                print(f"{nome_en} -> {nome_pt}")
            print("-" * 40)
            
        except Exception as e:
            print(f"Erro ao processar lote: {e}")
            erros += 1
            if erros > 5:
                print("Muitos erros consecutivos. Parando...")
                break
            time.sleep(5)
            continue
        
        # Verifica se ainda há registros para traduzir
        cursor.execute('SELECT COUNT(*) FROM alimentos WHERE traduzido = 0')
        restantes = cursor.fetchone()[0]
        if restantes == 0:
            break
            
        # Espera entre as requisições
        time.sleep(2)
    
    print(f"\nProcesso concluído!")
    print(f"Total traduzido nesta sessão: {traduzidos}")
    print(f"Erros encontrados: {erros}")
    
    conn.close()

if __name__ == "__main__":
    continuar_traducao() 