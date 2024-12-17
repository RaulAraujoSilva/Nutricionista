import streamlit as st
from database import BancoDados
from models import ItemRefeicao, Refeicao, UnidadeMedida
from avaliador import AvaliadorNutricional
from typing import List, Dict

# Configuração da página
st.set_page_config(
    page_title="Avaliador Nutricional",
    page_icon="🍽️",
    layout="wide"
)

# Inicialização do banco de dados e avaliador
@st.cache_resource
def carregar_banco():
    return BancoDados('banco_nutricional_completo.csv')

@st.cache_resource
def carregar_avaliador():
    return AvaliadorNutricional()

db = carregar_banco()
avaliador = carregar_avaliador()

# Inicialização da sessão
if 'refeicao_atual' not in st.session_state:
    st.session_state.refeicao_atual = Refeicao("Minha Refeição", [])
if 'observacoes' not in st.session_state:
    st.session_state.observacoes = ""

def adicionar_item():
    if st.session_state.alimento_selecionado and st.session_state.quantidade > 0:
        id_alimento = st.session_state.alimento_selecionado.split(" (")[-1].rstrip(")")
        alimento = db.buscar_por_id(id_alimento)
        if alimento:
            item = ItemRefeicao(
                alimento=alimento,
                quantidade=st.session_state.quantidade,
                unidade=UnidadeMedida.GRAMAS
            )
            st.session_state.refeicao_atual.adicionar_item(item)
            # Limpa os campos
            st.session_state.quantidade = None
            st.session_state.alimento_selecionado = None

def main():
    st.title("🍽️ Avaliador Nutricional")
    
    # Área de busca e adição de alimentos
    st.header("Adicionar Alimentos")
    
    # Campo de busca centralizado
    termo_busca = st.text_input("Buscar alimento:", key="termo_busca")
    
    if termo_busca:
        resultados = db.buscar_alimento(termo_busca)
        if resultados:
            # Campos de seleção e quantidade lado a lado
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                opcoes = {f"{a.nome} ({a.id})": a.id for a in resultados}
                st.selectbox(
                    "Selecione o alimento:",
                    options=list(opcoes.keys()),
                    key="alimento_selecionado",
                    format_func=lambda x: x.split(" (")[0]
                )
            
            with col2:
                st.number_input(
                    "Quantidade (g):",
                    min_value=0.0,
                    step=10.0,
                    key="quantidade",
                    value=None
                )
            
            with col3:
                st.write("")  # Espaço para alinhar com os outros campos
                st.button("Adicionar", on_click=adicionar_item, use_container_width=True)
        else:
            st.warning("Nenhum alimento encontrado")
    
    # Área principal - Lista de itens e avaliação
    st.header("Composição da Refeição")
    
    if not st.session_state.refeicao_atual.itens:
        st.info("Adicione alimentos à sua refeição usando o campo de busca acima")
    else:
        # Lista de itens
        for idx, item in enumerate(st.session_state.refeicao_atual.itens):
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.text(f"{item.alimento.nome}")
            with cols[1]:
                st.text(f"{item.quantidade}g")
            with cols[2]:
                if st.button("Remover", key=f"rem_{idx}"):
                    st.session_state.refeicao_atual.remover_item(idx)
                    st.rerun()
        
        # Campo de observações
        st.text_area(
            "Observações sobre a refeição (ex: horário, contexto, objetivos):",
            key="observacoes",
            height=100
        )
        
        # Resumo nutricional
        st.subheader("Resumo Nutricional")
        nutrientes = st.session_state.refeicao_atual.calcular_total_nutrientes()
        status = avaliador.verificar_limites(nutrientes)
        
        cols = st.columns(5)
        for idx, (nutriente, valor) in enumerate(nutrientes.items()):
            with cols[idx]:
                st.metric(
                    f"{nutriente.title()} ({status[nutriente]})", 
                    f"{valor:.1f}{'g' if nutriente != 'calorias' else ' kcal'}",
                    delta="↑" if status[nutriente] == "alto" else "↓" if status[nutriente] == "baixo" else "→"
                )
        
        # Botão de avaliação
        if st.button("Avaliar Refeição", type="primary"):
            with st.spinner("Analisando sua refeição..."):
                # Cria uma cópia da refeição com as observações
                refeicao = st.session_state.refeicao_atual
                refeicao.observacoes = st.session_state.get('observacoes', '')
                
                # Chama o método apenas com a refeição
                resultado = avaliador.avaliar_refeicao(refeicao)
                
                if resultado["sucesso"]:
                    st.markdown("### Avaliação Nutricional")
                    st.markdown(resultado["avaliacao"])
                else:
                    st.error(f"Erro ao avaliar refeição: {resultado['erro']}")

if __name__ == "__main__":
    main() 