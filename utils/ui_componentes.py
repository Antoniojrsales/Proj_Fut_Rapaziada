import streamlit as st

def render_card(title: str, value, gradient: str, prefix: str = "R$ ", is_currency: bool = True):
    """
    Renderiza um card estilizado com gradiente CSS.
    
    :param title: Título do Card (ex: "🟢 Lucro Greens")
    :param value: Valor numérico ou string
    :param gradient: Cores do gradiente CSS (ex: "#11998e, #38ef7d")
    :param prefix: Prefixo opcional (default: "R$ ")
    :param is_currency: Se True, formata como moeda brasileira. Se False, exibe o valor direto.
    """
    # Formatação condicional do valor
    if is_currency and isinstance(value, (int, float)):
        valor_formatado = f"{prefix}{value:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')
    else:
        valor_formatado = f"{value}"

    # Estilização CSS do Card
    card_style = f"""
        background: linear-gradient(135deg, {gradient});
        color: white;
        padding: 18px 20px;
        border-radius: 12px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        margin-bottom: 15px;
    """
    
    title_style = """
        font-size: 0.95em;
        font-weight: 500;
        opacity: 0.9;
        letter-spacing: 0.5px;
    """

    saldo_style = """
        font-size: 1.6em;
        font-weight: 700;
        margin-top: 6px;
    """

    st.markdown(f"""
        <div style="{card_style}">
            <div style="{title_style}">{title}</div>
            <div style="{saldo_style}">{valor_formatado}</div>
        </div>
    """, unsafe_allow_html=True)