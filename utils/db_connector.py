#-- 📚 Bibliotecas --#
import streamlit as st
import pandas as pd
import gspread

#-- 🗂️ Acessa as credenciais do secrets.toml --#
try:
    GSPREAD_CREDENTIALS = st.secrets["GSPREAD"]
    SHEET_ID = st.secrets["SHEET"]["SHEET_ID"]
    SHEET_NAME = st.secrets["SHEET"]["SHEET_NAME"]
except Exception as e:
    GSPREAD_CREDENTIALS = None
    SHEET_ID = None
    SHEET_NAME = None

@st.cache_resource
def get_gspread_client():
    """Conecta ao Google Sheets API e retorna a planilha acessada."""
    if GSPREAD_CREDENTIALS and SHEET_ID:
        try:
            # Usar st.cache_resource garante que a conexão só seja estabelecida uma vez por sessão
            gc = gspread.service_account_from_dict(GSPREAD_CREDENTIALS)
            sheet = gc.open_by_key(SHEET_ID)
            return sheet, True
        except Exception as e:
            st.error(f"❌ Erro ao conectar com o Google Sheets: {e}")
            return None, False
    return None, False

@st.cache_data(ttl=600)
def load_data(sheet_name, _sheet_client):
    """Carrega dados da planilha para um DataFrame do Pandas."""
    if not _sheet_client:
        return pd.DataFrame()
    try:
        ws = _sheet_client.worksheet(sheet_name)
        data = ws.get_all_values()
        
        if not data:
            return pd.DataFrame()
        
        # Separa o cabeçalho das demais linhas
        cols = data.pop(0)
        df = pd.DataFrame(data, columns=cols)
        
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar a aba '{sheet_name}': {e}")
        return pd.DataFrame()

def append_row(new_row: list, _sheet_client):
    """
    Insere uma nova linha na aba principal da planilha e invalida apenas o cache de load_data.
    """
    if not _sheet_client:
        return False

    try:
        target_sheet = SHEET_NAME or st.secrets["SHEET"]["SHEET_NAME"]
        ws = _sheet_client.worksheet(target_sheet)
        
        # Insere a nova linha formatando os dados conforme digitados pelo usuário
        ws.append_row(new_row, value_input_option='USER_ENTERED')
        
        # 🎯 MELHORIA: Limpa APENAS o cache da função load_data em vez de resetar o app todo
        load_data.clear()

        return True

    except Exception as e:
        st.error(f"❌ Erro ao adicionar dados na planilha: {e}")
        return False