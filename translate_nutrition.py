import pandas as pd
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

def traduzir_lote(items: List[str], max_retries: int = 3) -> List[str]:
    """
    Traduz um lote de itens usando a API do OpenAI com GPT-4o-mini
    """
    prompt = "Traduza os seguintes alimentos para português brasileiro. Retorne apenas as traduções, uma por linha:\n\n"
    prompt += "\n".join(items)
    
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um tradutor especializado em nomes de alimentos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            # Extrai as traduções da resposta
            traducoes = response.choices[0].message.content.strip().split('\n')
            if len(traducoes) != len(items):
                print(f"Aviso: Número de traduções ({len(traducoes)}) diferente do número de itens ({len(items)})")
                return items
            return traducoes
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Erro após {max_retries} tentativas: {e}")
                return items
            time.sleep(3)
    
    return items

def processar_arquivo():
    # Lê o arquivo CSV
    df = pd.read_csv('Nutriction Dataset.csv')
    
    # Cria uma cópia da coluna Food para backup
    df['Nome_PT'] = df['Food'].copy()
    
    # Processa em lotes pequenos devido às limitações do modelo mini
    tamanho_lote = 5  # Reduzido para 5 itens por lote
    total_items = len(df)
    
    for i in range(0, total_items, tamanho_lote):
        # Pega o próximo lote
        lote = df['Food'].iloc[i:i+tamanho_lote].tolist()
        
        # Traduz o lote
        traducoes = traduzir_lote(lote)
        
        # Atualiza as traduções no DataFrame
        df.loc[i:i+tamanho_lote-1, 'Nome_PT'] = traducoes
        
        # Salva o progresso frequentemente
        if i % 25 == 0:  # Salva a cada 25 itens
            df.to_csv('Nutriction Dataset_PT.csv', index=False)
            print(f"Progresso: {i}/{total_items} itens processados")
        
        # Intervalo entre lotes
        time.sleep(1.5)
    
    # Salva o arquivo final
    df.to_csv('Nutriction Dataset_PT.csv', index=False)
    print("Processamento concluído!")

if __name__ == "__main__":
    processar_arquivo() 