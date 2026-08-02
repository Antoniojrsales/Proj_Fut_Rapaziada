import streamlit as st

def check_login():
    """Verifica se o usuário está autenticado antes de renderizar a página."""
    if not st.session_state.get('logged_in', False):
        st.warning("🔒 Você precisa estar logado para acessar esta página.")
        st.info("Por favor, acesse a página de login para continuar.")
        st.stop()