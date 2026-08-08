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
from utils.grafics import jogos_dia_seguinte

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
    page_title="Visualização dos Dados | Dados Futebol Rapaziada",
    page_icon="🎲",
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

aba1 = st.columns(1)[0]
#Criando uma tabela para visualizar os jogos do dia seguinte
with aba1:
    st.markdown("<h3 style='text-align: center;'>⚽ Jogos do Dia Seguinte</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin: 0; padding: 10px; margin-bottom: 20px;'>Tabela que mostra os dados dos jogos do dia seguinte incluindo informações como data, mercado, campeonato, times, placar, odd e stake</p>", unsafe_allow_html=True)

    # Exibe a tabela com os dados dos jogos do dia seguinte
    jogos_dia_seguinte(df_dados)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📑 ESTRUTURA DE NAVEGAÇÃO (TABS)
# ---------------------------------------------------------
# 1. Cria as abas de 'Dados Brutos' e 'Inserção'
# 2. Aplica o arquivo de estilos CSS local
aba2, aba3 = st.tabs(['Dados Brutos', 'Inserindo Dados na base'])
local_css("style.css")

# ---------------------------------------------------------
# 🔍 ABA 1: VISUALIZAÇÃO E FILTRAGEM
# ---------------------------------------------------------
# 1. Filtros laterais para selecionar colunas e tipo de visualização (Top/Bottom)
# 2. Aplica configurações de formatação de moeda (R$) na coluna de valores
# 3. Exibe o resumo quantitativo (linhas e colunas) do dataset
with aba2:
    st.markdown("<h3 style='text-align: center;'>🎲 Visualização dos Dados</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin: 0; padding: 10px; margin-bottom: 20px;'>Tabela que mostra os dados brutos de jogos, incluindo informações como data, mercado, campeonato, times, placar, odd e stake e metricas para análise.</p>", unsafe_allow_html=True)

    with st.sidebar.expander("🔍 Visualizar colunas"):
        options = st.multiselect('Escolha a Coluna:', df_dados.columns, default=list(df_dados.columns))

    options_dados = st.sidebar.radio('Escolha qual o filtro de visualização:',
                            ['Todos', 'Head', 'Tail'])

    if options:
        df_filtrado = df_dados[options]

        # Adicione a formatação de moeda para a coluna Valor
        column_config = {
            "Valor": st.column_config.NumberColumn(
                "Valor",
                format="R$ %0.2f",
                help="Valor do gasto ou receita"
            )
        }
        if options_dados == 'Todos':
            st.dataframe(df_filtrado, column_config=column_config)
        elif options_dados == 'Head':
            st.dataframe(df_filtrado.head(10), column_config=column_config)
        else:
            st.dataframe(df_filtrado.tail(10), column_config=column_config)
    else:
        st.write('Por favor, selecione ao menos uma coluna.')

    st.divider()
    st.markdown("Dimensões do DataFrame:")
    st.markdown(f"Linhas: \t {df_dados.shape[0]}")
    st.markdown(f"Colunas: \t {df_dados.shape[1]}")
    st.divider()

# ---------------------------------------------------------
# 📝 ABA 2: FORMULÁRIO DE ENTRADA DE DADOS
# ---------------------------------------------------------
with aba3:
    st.subheader("➕ Adicionar Nova Entrada de Jogo")
    st.write("Preencha os dados da partida para atualizar a base do Google Sheets.")

    # 1. Carrega opções dinâmicas dos mercados existentes (ou define padrão)
    if 'Mercado' in df_dados.columns:
        tipos_mercados_disponiveis = sorted(df_dados['Mercado'].unique().tolist())
    else:
        tipos_mercados_disponiveis = ['Over0.5_3porc', 'Under6.5_3porc']

    sheet_client, connected = get_gspread_client()

    # 2. Formulário Estruturado em Blocos Visuais
    with st.form("form_novo_jogo", clear_on_submit=True):
        
        # --- Linha 1: Informações da Partida ---
        col_data, col_mercado, col_campeonato = st.columns(3)
        with col_data:
            select_data = st.date_input('📅 Data:', datetime.now().date())
        with col_mercado:
            select_mercado = st.selectbox(
                '🎯 Mercado:', 
                options=tipos_mercados_disponiveis, 
                index=None, 
                placeholder='Escolha um mercado...'
            )
        with col_campeonato:
            select_campeonato = st.text_input('🏆 Campeonato:', placeholder='Ex: China, Amistosos, etc.')

        # --- Linha 2: Confronte e Placar ---
        col_timeKs, col_Xks, col_Xfora, col_timefora = st.columns([3, 1.5, 1.5, 3])
        with col_timeKs:
            select_time_ks = st.text_input('🏠 Time Mandante (Time_Ks):', placeholder='Ex: Henan Songshan')

        # No formulário:
        jogo_finalizado = st.checkbox("Jogo já finalizado?")

        if jogo_finalizado:
            col_Xks, col_Xfora = st.columns(2)
            with col_Xks:
                select_x_ks = st.number_input('Gols Mandante:', min_value=0, step=1, value=0)
            with col_Xfora:
                select_x_fora = st.number_input('Gols Visitante:', min_value=0, step=1, value=0)
            
            gols_ks_val = str(int(select_x_ks))
            gols_fora_val = str(int(select_x_fora))
        else:
            # Se o jogo é futuro, grava células vazias na planilha
            gols_ks_val = ""
            gols_fora_val = ""

        with col_timefora:
            select_time_fora = st.text_input('✈️ Time Visitante (Time_Fora):', placeholder='Ex: Dalian Yingbo')

        # --- Linha 3: Odds e Gestão (Stake) ---
        col_odd, col_stake = st.columns(2)
        with col_odd:
            select_odd = st.number_input('📈 Odd (%):', min_value=0.0, step=0.5, value=2.0, format="%.1f")
        with col_stake:
            select_stake = st.number_input('💵 Stake (R$):', min_value=0.1, step=1.0, value=3.0, format="%.2f")

        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.form_submit_button('💾 Salvar Registro na Base', use_container_width=True)

        # 🎨 Estilização do Botão
        st.markdown("""
        <style>
        .stFormSubmitButton > button {
            background-color: #075eb2 !important;
            color: white !important;
            border-radius: 6px;
            font-weight: bold;
            padding: 0.6em 1em;
        }
        .stFormSubmitButton > button:hover {
            background-color: #004d9f !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 💾 LÓGICA DE PROCESSAMENTO E ENVIO
    # ---------------------------------------------------------
    if submit_button:
        if not connected:
            st.error("❌ Conexão com o Google Sheets falhou. Tente novamente mais tarde.")
        elif not select_mercado:
            st.warning("⚠️ Por favor, selecione um Mercado.")
        elif not select_campeonato or not select_time_ks or not select_time_fora:
            st.warning("⚠️ Preencha os nomes do Campeonato e dos Times.")
        else:
            # Formata a data para DD/MM conforme o padrão da planilha
            data_formatada = select_data.strftime("%d/%m")
            
            # Formata a stake para o padrão R$ X,XX igual ao salvo na planilha
            stake_formatada = f"R$ {select_stake:.2f}".replace('.', ',')

            # Ordem EXATA das colunas da planilha:
            # [Data, Mercado, Campeonato, Time_Ks, X_Ks, X_Fora, Time_Fora, Odd %, Stake]
            nova_linha = [
                data_formatada,
                select_mercado,
                select_campeonato.strip(),
                select_time_ks.strip(),
                gols_ks_val,
                gols_fora_val,
                select_time_fora.strip(),
                select_odd,
                stake_formatada
            ]

            with st.spinner("Enviando dados para o Google Sheets..."):
                if append_row(nova_linha, sheet_client):
                    st.success("✅ Partida registrada com sucesso na planilha!")
                    
                    # Recarrega e reprocessa a base inteira para atualizar gráficos e tabelas
                    df_bruto = load_data(st.secrets["SHEET"]["SHEET_NAME"], sheet_client)
                    st.session_state['df_Bi_Gastos_Resid'] = process_data(df_bruto)
                    st.rerun()
                else:
                    st.error("❌ Falha ao salvar no Google Sheets. Verifique o console.")