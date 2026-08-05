# ---------------------------------------------------------
# 📚 BIBLIOTECAS E RECURSOS INTERNOS
# ---------------------------------------------------------
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth_check import check_login
from utils.db_connector import get_gspread_client, append_row, load_data
from utils.data_processing import process_data
from utils.processing_data_lay import processar_regras_lay
from utils.metrics import grafico_rank_mercados, grafico_contagem_mercados

# 1. Garante que o usuário está autenticado logo no topo
check_login()

# 2. Botão de Logout na Sidebar (Menu Lateral)
with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Sair da Conta", use_container_width=True, type="primary"):
        st.session_state.clear()
        st.switch_page("1_🗝️_login.py")

# ---------------------------------------------------------
# ⚙️ CONFIGURAÇÕES INICIAIS DA INTERFACE (STREAMLIT)
# ---------------------------------------------------------
# 1. Define o título da aba e o ícone da aplicação
# 2. Configura o layout como 'wide' para usar toda a largura da tela
# 3. Adiciona os créditos do desenvolvedor na barra lateral
st.set_page_config(
    page_title="Tendências | Dados Futebol Rapaziada",
    page_icon="📊",
    layout="wide"
)
st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')

# ---------------------------------------------------------
# 🎨 ESTILIZAÇÃO E CABEÇALHO HTML
# ---------------------------------------------------------
# 1. Função para carregar arquivo CSS externo
# 2. Renderiza o título principal da página usando tags HTML/CSS personalizadas
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div style="
    padding: 5px;
    text-align: center;">
    <h2 style=" font-size: 40px; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif">
                Tendências | Dados Futebol Rapaziada</h2>
    <div id="chart-container" style="color:'blue'"></div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# 🔐 SEGURANÇA E CONTROLE DE SESSÃO
# ---------------------------------------------------------
# 1. Verifica se o usuário está logado
# 2. Inicializa chaves de controle no session_state para reset de formulários
# 3. Valida se os dados necessários existem na memória antes de prosseguir
check_login()

if 'df_Bi_Fut_Rapaziada' in st.session_state:
    # 1. Pega os dados brutos da sessão
    df_dados = st.session_state['df_Bi_Fut_Rapaziada']

    # 2. Aplica o processamento das regras de Lay que acabamos de validar no terminal
    df_dados = processar_regras_lay(df_dados)

    # 3. Atualiza a sessão para que os cards e a tabela recebam os dados atualizados
    st.session_state['df_Bi_Fut_Rapaziada'] = df_dados
else:
    st.warning("Dados não encontrados na sessão. Por favor, faça login novamente.")

if df_dados.empty:    
    st.warning("Dados não encontrados na sessão. Por favor, faça login novamente.")
    st.stop()

colbarramercados, colbarraacertos = st.columns([1, 1])

with colbarramercados:    
    # Usa direto a chave do dicionario retornado pela funcao
    grafico_rank_mercados(st.session_state["df_Bi_Fut_Rapaziada"])

with colbarraacertos:
    grafico_contagem_mercados(st.session_state["df_Bi_Fut_Rapaziada"])

st.markdown("---")