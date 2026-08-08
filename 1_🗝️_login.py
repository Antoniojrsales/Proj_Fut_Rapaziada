# ---------------------------------------------------------
# 📚 BIBLIOTECAS E RECURSOS INTERNOS
# ---------------------------------------------------------
import streamlit as st
import hashlib
import hmac
from utils.db_connector import get_gspread_client, load_data, SHEET_NAME 
from utils.data_processing import process_data

# ---------------------------------------------------------
# ⚙️ CONFIGURAÇÕES INICIAIS DA INTERFACE (STREAMLIT)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Login | Dados Futebol Rapaziada", 
    page_icon="🔐", 
    layout="centered"
)

with st.sidebar:
    with st.expander("ℹ️ Sobre o Sistema"):
        st.markdown(
            """
            Plataforma de análise para acompanhamento de desempenho, tendências e métricas do Mercado da Bola Mundial.

            **Mercados Analisados:**
            * **Over 0.5:** Entrada para +0.5 gols na partida (retorno até 3%).
            * **Under 6.5:** Entrada para -6.5 gols na partida (retorno até 3%).
            * **Lay ao Placar:** Contra um placar específico (stake base de R$ 1,00).
            """
        )

st.sidebar.markdown('Desenvolvido por [AntonioJrSales](https://antoniojrsales.github.io/meu_portfolio/)')


# ---------------------------------------------------------
# 🎨 UTILITÁRIOS DE ESTILIZAÇÃO (CSS)
# ---------------------------------------------------------
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# ---------------------------------------------------------
# 🔐 LÓGICA DE AUTENTICAÇÃO E SEGURANÇA
# ---------------------------------------------------------
def check_password(input_password, stored_password):
    """Compara o hash da senha digitada com a armazenada usando hmac."""
    input_hash = hashlib.sha256(input_password.encode()).hexdigest()
    return hmac.compare_digest(input_hash, stored_password)

# ---------------------------------------------------------
# 🗂️ CARREGAR CREDENCIAIS DE USUÁRIO
# ---------------------------------------------------------
try:
    USERS = st.secrets["AUTH_USERS"]
except KeyError:
    st.error("❌ Credenciais de usuário ausentes no secrets.toml.")
    st.stop()

# ---------------------------------------------------------
# 🔗 CONEXÃO COM A BASE DE DADOS (GOOGLE SHEETS)
# ---------------------------------------------------------
sheet_client, connected = get_gspread_client()

# Exibe aviso apenas se houver falha de conexão na abertura
if not connected:
    st.warning("⚠️ O sistema de banco de dados está indisponível no momento.")

# ---------------------------------------------------------
# 🎨 RENDERIZAÇÃO DO FORMULÁRIO DE LOGIN
# ---------------------------------------------------------
local_css('style_button_login.css')

with st.form("login_form"):
    st.markdown("<h1 style='text-align: center;'>🔐 Login</h1>", unsafe_allow_html=True)
    st.divider()

    username = st.text_input("👤 Usuário").strip()
    password = st.text_input("🔒 Senha", type="password").strip()

    submit = st.form_submit_button("Entrar", use_container_width=True)

# ---------------------------------------------------------
# 🚀 VALIDAÇÃO E PROCESSAMENTO DO LOGIN
# ---------------------------------------------------------
if submit:
    if not connected:
        st.error("❌ Não foi possível conectar à base de dados. Tente novamente mais tarde.")
    elif username in USERS and check_password(password, USERS[username]):
        
        # Carrega os dados para a sessão
        with st.spinner("Autenticando e carregando dados..."):
            df_bruto = load_data(SHEET_NAME, sheet_client)
            
            if not df_bruto.empty:
                df_dados = process_data(df_bruto)
                
                # Salva o estado da sessão
                st.session_state['logged_in'] = True
                st.session_state['df_Bi_Fut_Rapaziada'] = df_dados
                st.session_state['username'] = username
                
                st.success("✅ Login bem-sucedido!")
                
                # Exemplo de navegação nativa do Streamlit (descomente e ajuste o caminho da página):
                st.switch_page("pages/2_🏠_painel.py")
            else:
                st.warning("⚠️ Planilha vazia ou sem dados válidos.")
    else:
        st.error("❌ Usuário ou senha inválidos.")