import os
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI
from models import Refeicao

# Carrega as variáveis de ambiente
load_dotenv()

# Inicializa o cliente OpenAI (usará OPENAI_API_KEY do ambiente automaticamente)
client = OpenAI()

class AvaliadorNutricional:
    def __init__(self):
        self.valores_referencia = {
            "calorias": {
                "min": 400,  # kcal por refeição principal
                "max": 800
            },
            "proteinas": {
                "min": 15,  # gramas
                "max": 30
            },
            "carboidratos": {
                "min": 45,  # gramas
                "max": 90
            },
            "gorduras": {
                "min": 10,  # gramas
                "max": 25
            },
            "fibras": {
                "min": 6,  # gramas
                "max": 12
            }
        }
    
    def _gerar_prompt(self, refeicao: Refeicao) -> str:
        """Gera o prompt para o LLM baseado na refeição"""
        resumo = refeicao.gerar_resumo()
        nutrientes = refeicao.calcular_total_nutrientes()
        observacoes = refeicao.observacoes.strip() if refeicao.observacoes else "Nenhuma observação fornecida."
        
        prompt = f"""Analise a seguinte refeição e forneça uma avaliação nutricional detalhada em português, considerando especialmente o contexto e as observações do usuário.

IMPORTANTE: Sua resposta DEVE seguir EXATAMENTE a estrutura abaixo, incluindo todos os tópicos numerados.

DADOS DA REFEIÇÃO:
{resumo}

CONTEXTO E OBSERVAÇÕES DO USUÁRIO:
{observacoes}

VALORES DE REFERÊNCIA:
- Calorias: {self.valores_referencia['calorias']['min']}-{self.valores_referencia['calorias']['max']} kcal
- Proteínas: {self.valores_referencia['proteinas']['min']}-{self.valores_referencia['proteinas']['max']}g
- Carboidratos: {self.valores_referencia['carboidratos']['min']}-{self.valores_referencia['carboidratos']['max']}g
- Gorduras: {self.valores_referencia['gorduras']['min']}-{self.valores_referencia['gorduras']['max']}g
- Fibras: {self.valores_referencia['fibras']['min']}-{self.valores_referencia['fibras']['max']}g

ESTRUTURA OBRIGATÓRIA DA RESPOSTA:

1. ANÁLISE GERAL:
   - Composição geral da refeição
   - Adequação ao contexto fornecido pelo usuário
   - Balanço nutricional geral

2. PONTOS POSITIVOS:
   - Aspectos nutricionais positivos
   - Escolhas alimentares benéficas
   - Adequação ao contexto/objetivos do usuário

3. PONTOS DE ATENÇÃO:
   - Possíveis desequilíbrios nutricionais
   - Inadequações considerando o contexto
   - Riscos potenciais

4. RECOMENDAÇÕES:
   - Sugestões específicas de melhorias
   - Ajustes baseados no contexto e objetivos
   - Alternativas e complementos recomendados

5. ANÁLISE DA OBSERVAÇÃO:
   - Faça referência explícita ao que foi pedido pelo usuário
   - Dê uma resposta no contexto da refeição
   - Esclareça as questões levantadas pelo usuário

6. AVALIAÇÃO FINAL:
   - Nota geral (0-10)
   - Justificativa da nota
   - Resumo das principais recomendações

LEMBRE-SE:
- Use EXATAMENTE os números e títulos das seções acima
- Inclua TODAS as seções, mesmo que algumas observações sejam breves
- Mantenha um tom construtivo e educativo
- Seja específico ao abordar as observações do usuário"""

        return prompt
    
    def avaliar_refeicao(self, refeicao: Refeicao) -> Dict:
        """Avalia a refeição usando o LLM e retorna o resultado
        
        Args:
            refeicao: A refeição a ser avaliada (incluindo observações do usuário)
        """
        prompt = self._gerar_prompt(refeicao)
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """Você é um nutricionista experiente especializado em avaliação de refeições.
                        
INSTRUÇÕES IMPORTANTES:
1. Siga EXATAMENTE a estrutura fornecida no prompt
2. Inclua TODAS as seções numeradas
3. Mantenha os mesmos títulos das seções
4. Não pule ou combine seções
5. Dê atenção especial à seção 5 (ANÁLISE DA OBSERVAÇÃO)
6. Seja específico ao responder às questões do usuário

Sua análise deve ser:
1. Personalizada ao contexto do usuário
2. Cientificamente embasada
3. Prática e aplicável
4. Construtiva e motivadora
5. Clara e estruturada"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=2000
            )
            
            avaliacao = chat_completion.choices[0].message.content
            
            return {
                "sucesso": True,
                "avaliacao": avaliacao,
                "erro": None
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "avaliacao": None,
                "erro": str(e)
            }
    
    def verificar_limites(self, nutrientes: Dict[str, float]) -> Dict[str, str]:
        """Verifica se os nutrientes estão dentro dos limites recomendados"""
        status = {}
        
        for nutriente, valor in nutrientes.items():
            if valor < self.valores_referencia[nutriente]['min']:
                status[nutriente] = "baixo"
            elif valor > self.valores_referencia[nutriente]['max']:
                status[nutriente] = "alto"
            else:
                status[nutriente] = "adequado"
        
        return status