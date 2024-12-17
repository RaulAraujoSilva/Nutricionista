from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class UnidadeMedida(Enum):
    GRAMAS = "g"
    MILILITROS = "ml"
    UNIDADE = "un"
    PORCAO = "porção"

@dataclass
class AlimentoBase:
    """Representa um alimento da base de dados"""
    id: str
    nome: str
    nome_en: str
    calorias: float  # kJ
    proteinas: float  # g
    carboidratos: float  # g
    gorduras: float  # g
    fibras: float  # g
    unidade_padrao: UnidadeMedida
    porcao_padrao: float  # em gramas ou ml

@dataclass
class ItemRefeicao:
    """Representa um item específico em uma refeição"""
    alimento: AlimentoBase
    quantidade: float
    unidade: UnidadeMedida
    
    def calcular_nutrientes(self) -> Dict[str, float]:
        """Calcula os nutrientes baseado na quantidade"""
        fator = self.quantidade / self.alimento.porcao_padrao
        return {
            "calorias": self.alimento.calorias * fator,
            "proteinas": self.alimento.proteinas * fator,
            "carboidratos": self.alimento.carboidratos * fator,
            "gorduras": self.alimento.gorduras * fator,
            "fibras": self.alimento.fibras * fator
        }

@dataclass
class Refeicao:
    """Representa uma refeição completa"""
    nome: str
    itens: List[ItemRefeicao]
    observacoes: str = ""  # Campo para observações do usuário
    
    def adicionar_item(self, item: ItemRefeicao):
        self.itens.append(item)
    
    def remover_item(self, index: int):
        if 0 <= index < len(self.itens):
            self.itens.pop(index)
    
    def calcular_total_nutrientes(self) -> Dict[str, float]:
        """Calcula o total de nutrientes da refeição"""
        totais = {
            "calorias": 0.0,
            "proteinas": 0.0,
            "carboidratos": 0.0,
            "gorduras": 0.0,
            "fibras": 0.0
        }
        
        for item in self.itens:
            nutrientes = item.calcular_nutrientes()
            for key in totais:
                totais[key] += nutrientes[key]
        
        return totais
    
    def gerar_resumo(self) -> str:
        """Gera um resumo da refeição para avaliação"""
        resumo = f"Refeição: {self.nome}\n\n"
        resumo += "Itens:\n"
        
        for item in self.itens:
            resumo += f"- {item.alimento.nome}: {item.quantidade}{item.unidade.value}\n"
        
        nutrientes = self.calcular_total_nutrientes()
        resumo += "\nTotais:\n"
        for nutriente, valor in nutrientes.items():
            resumo += f"- {nutriente}: {valor:.1f}\n"
        
        return resumo 