import pandas as pd
import plotly.express as px
import streamlit as st
from utils.metrics import metricas_gerais
from utils.auth_check import check_login
from utils.ui_componentes import render_card

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
    page_title="Painel Geral | Futebol Rapaziada",
    page_icon="🏠",
    layout="wide"
)
st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')

# ---------------------------------------------------------
# 🎨 ESTILIZAÇÃO E IDENTIDADE VISUAL (CSS/HTML)
# ---------------------------------------------------------
# 1. Renderiza o título principal centralizado via HTML
# 2. Aplica fontes personalizadas e espaçamentos
# 3. Executa a verificação de autenticação do usuário
st.markdown("""
<div style="padding: 5px; text-align: center;">
    <h2 style=" font-size: 40px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif">
        Painel Geral | Futebol Rapaziada
    </h2>
    <div id="chart-container" style="margin-bottom: 30px; color:'blue'"></div>
</div>
""", unsafe_allow_html=True)

check_login()

# ---------------------------------------------------------
# 🗂️ GESTÃO DE DADOS DA SESSÃO
# ---------------------------------------------------------
# 1. Verifica se o DataFrame principal existe no estado da sessão
# 2. Atribui os dados à variável local 'df_dados'
# 3. Emite um aviso caso os dados não sejam localizados
if 'df_Bi_Fut_Rapaziada' in st.session_state:
    df_dados = st.session_state['df_Bi_Fut_Rapaziada']
else:
    st.warning("Dados não encontrados na sessão. Por favor, faça login novamente.")

banca = 100
m = metricas_gerais(df_dados)

st.subheader("📌 Resumo Geral da Banca")

colbanca, colgr, colvazio2, clovazio3 = st.columns([3, 2, 3, 2])
# 🟢 Linha 1: Card em Destaque (Banca / Lucro Total)
# Gradiente Azul Escuro -> Roxo
with colbanca:
    render_card(
        title="💰 BANCA ATUAL (ou Saldo Atual)",
        value= banca + (m['lucro_total']),
        gradient="#2b5876, #4e4376"
    )

with colgr:
    render_card(
        title="📈 LUCRO / PREJUÍZO LÍQUIDO",
        value=m['lucro_total'],
        gradient="#4e4376, #2b5876"
    )

st.markdown("---")

st.subheader("📊 Métricas Gerais do Período")

# 🟢 Linha 2: Os 4 Cards em Colunas
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    # Gradiente Verde
    render_card(
        title="🟢 Lucro Greens",
        value=m['total_greens_rs'],
        gradient="#11998e, #38ef7d"
    )

with col2:
    # Gradiente Vermelho
    render_card(
        title="🔴 Prejuízo Reds",
        value=m['total_reds_rs'],
        gradient="#cb2d3e, #ef473a"
    )

with col3:
    # Gradiente Azul (Sem formatação R$)
    render_card(
        title="✅ Qtd. Greens",
        value=f"{m['total_green']} entradas",
        gradient="#2193b0, #6dd5ed",
        is_currency=False
    )

with col4:
    # Gradiente Laranja/Escuro (Sem formatação R$)
    render_card(
        title="❌ Qtd. Reds",
        value=f"{m['total_red']} entradas",
        gradient="#ff4e50, #f9d423",
        is_currency=False
    )

with col5:
    # Gradiente Roxo (Sem formatação R$)
    render_card(
        title="🎯 Taxa de Acerto",
        value=f"{m['taxa_acerto']:.2f}%",
        gradient="#8e2de2, #4a00e0",
        is_currency=False
    )

st.markdown("---")

st.subheader("📈 Métricas Avançadas do Período")
# 🟢 Linha 3: Os 5 Cards em Colunas
col6, col7, col8, col9, col10 = st.columns(5)
with col6:
    # Gradiente Azul Claro
    render_card(
        title="⚽ Jogos Pendentes",
        value=f"{m['total_pendentes']} entradas",
        gradient="#00c6ff, #0072ff",
        is_currency=False
    )

with col7:
    # Gradiente Verde Claro
    roi_fmt = f"{m['roi']:.2f}%".replace('.', ',')
    render_card(
        title="📈 Retorno Invest. (ROI)",
        value=roi_fmt,
        gradient="#11998e, #38ef7d" if m['roi'] >= 0 else "#cb2d3e, #ef473a",
        is_currency=False
    )