import pandas as pd
from typing import List, Optional
from models import AlimentoBase, UnidadeMedida

class BancoDados:
    def __init__(self, arquivo_csv: str):
        self.df = pd.read_csv(arquivo_csv, sep=';', encoding='utf-8-sig')
        self.alimentos: List[AlimentoBase] = self._carregar_alimentos()
        
    def _carregar_alimentos(self) -> List[AlimentoBase]:
        """Carrega os alimentos do CSV para a memória"""
        alimentos = []
        
        for _, row in self.df.iterrows():
            try:
                # Converte kJ para kcal (aproximadamente)
                calorias = float(row['Energywithdietaryfibre(kJ)']) * 0.239
                
                # Define unidade padrão baseado no nome/tipo do alimento
                unidade = UnidadeMedida.GRAMAS  # Padrão
                porcao = 100.0  # Padrão em gramas
                
                # Cria o objeto AlimentoBase
                alimento = AlimentoBase(
                    id=str(row['FoodID']),  # Convertendo para string
                    nome=str(row['Nome em Português']),
                    nome_en=str(row['FoodName']),
                    calorias=calorias,
                    proteinas=float(row['Protein(g)']),
                    carboidratos=float(row['Availablecarbohydrateswithsugaralcohols(g)']),
                    gorduras=float(row['Totalfat(g)']),
                    fibras=float(row['Dietaryfibre(g)']),
                    unidade_padrao=unidade,
                    porcao_padrao=porcao
                )
                alimentos.append(alimento)
            except Exception as e:
                print(f"Erro ao processar linha {row['FoodID']}: {str(e)}")
                continue
        
        return alimentos
    
    def buscar_alimento(self, termo: str) -> List[AlimentoBase]:
        """Busca alimentos pelo nome em português"""
        termo = termo.lower()
        return [
            alimento for alimento in self.alimentos
            if termo in alimento.nome.lower()
        ]
    
    def buscar_por_id(self, id: str) -> Optional[AlimentoBase]:
        """Busca um alimento específico pelo ID"""
        for alimento in self.alimentos:
            if alimento.id == id:
                return alimento
        return None
    
    def listar_todos_alimentos(self) -> List[AlimentoBase]:
        """Retorna a lista completa de alimentos"""
        return self.alimentos.copy()

# Exemplo de uso
if __name__ == "__main__":
    db = BancoDados('banco_nutricional_completo.csv')
    
    # Teste de busca
    resultados = db.buscar_alimento("arroz")
    for alimento in resultados:
        print(f"{alimento.nome} - {alimento.calorias:.1f} kcal/100g")