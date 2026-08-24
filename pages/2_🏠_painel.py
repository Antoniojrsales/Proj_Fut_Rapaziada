import pandas as pd
import plotly.express as px
import streamlit as st
from utils.metrics import metricas_gerais, renderizar_cards_metricas_mercados, calcular_drawdown, radar_gestao
from utils.auth_check import check_login
from utils.ui_componentes import render_card
from utils.processing_data_lay import processar_regras_lay

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

check_login()

# ---------------------------------------------------------
# 🗂️ GESTÃO DE DADOS DA SESSÃO
# ---------------------------------------------------------
# 1. Verifica se o DataFrame principal existe no estado da sessão
# 2. Atribui os dados à variável local 'df_dados'
# 3. Emite um aviso caso os dados não sejam localizados
if 'df_Bi_Fut_Rapaziada' in st.session_state:
    # 1. Pega os dados brutos da sessão
    df_dados = st.session_state['df_Bi_Fut_Rapaziada']

    # 2. Aplica o processamento das regras de Lay que acabamos de validar no terminal
    df_dados = processar_regras_lay(df_dados)

    # 3. Atualiza a sessão para que os cards e a tabela recebam os dados atualizados
    st.session_state['df_Bi_Fut_Rapaziada'] = df_dados
else:
    st.warning("Dados não encontrados na sessão. Por favor, faça login novamente.")

banca = 110
m = metricas_gerais(df_dados)

st.subheader("📌 Resumo Geral da Banca (Lucro liquido, ROI, Contagem Green/Reds, Mercados)")
col_banca, col_lucro, col_roi, col_green, col_red = st.columns([1.6, .9, 1.1, .7, .7])
with col_banca:
    banca_atual = banca + (m['lucro_total'])
    render_card(
        title="💰 BANCA ATUAL (ou Saldo Atual)",
        value= banca_atual,
        gradient="#2b5876, #4e4376"
    )

with col_lucro:
    st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1a2246 0%, #233161 100%); padding: 5px; border-radius: 10px; color: white; margin-bottom: 10px;">
                <p style="margin: 0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase; text-align: center; padding: 3px;">
                    📈 LUCRO / PREJUÍZO LÍQUIDO
                </p>
                <h4 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-align: center; padding: 3px;">
                   R$ {m['lucro_total']:.2f}
                </h4>
                <p style="margin: 0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase; text-align: center; padding: 3px;">
                    🏦 Porcentagem da Banca
                </p>
                <h4 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-align: center; padding: 3px;">
                    {m['porcentagem_banca']:.2f}%
                </h4>
            </div>
            """,
            unsafe_allow_html=True,)

cd = calcular_drawdown(df_dados)
with col_roi:
    roi_fmt = f"{m['roi']:.2f}%".replace('.', ',')
    st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1c2b54 0%, #253e74 100%); padding: 5px; border-radius: 10px; color: white; margin-bottom: 10px;">
                <h4 style="margin: 5px 0 0 0; font-size: 1rem; font-weight: bold; padding: 3px;">
                    💸ROI: {roi_fmt}
                </h4>
                <h4 style="margin: 5px 0 0 0; font-size: 1rem; font-weight: bold; padding: 3px;">
                    📉 Drawdown atual: R$ {cd['dd_atual_reais']:.2f}
                </h4>
                <h4 style="margin: 5px 0 0 0; font-size: 1rem; font-weight: bold; padding: 3px;">
                    📉 Drawdown % da banca: {cd['dd_atual_perc_banca']:.2f}%
                </h4>
                <h4 style="margin: 5px 0 0 0; font-size: 1rem; font-weight: bold; padding: 3px;">
                    🎯Taxa acerto: {m['taxa_acerto']:.2f}%
                </h4>
                <h4 style="margin: 5px 0 0 0; font-size: 1rem; font-weight: bold; padding: 3px;">
                    ⚽Jogos Pendentes: {m['total_pendentes']}
                </h4>
            </div>
            """,
            unsafe_allow_html=True,)

with col_green:
    st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1e335f 0%, #264a85 100%); padding: 5px; border-radius: 10px; color: white; margin-bottom: 10px;">
                <p style="margin: 0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase; text-align: center; padding: 3px;">
                    🟢 Lucro Greens
                </p>
                <h4 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-align: center; padding: 3px;">
                    R$ {m['total_greens_rs']:.2f}
                </h4>
                <p style="margin: 0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase; text-align: center; padding: 3px;">
                    🔴 Prejuízo Reds
                </p>
                <h4 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-align: center; padding: 3px;">
                    R$ {m['total_reds_rs']:.2f}
                </h4>
            </div>
            """,
            unsafe_allow_html=True,)

with col_red:
    st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #223a6c 0%, #295596 100%); padding: 5px; border-radius: 10px; color: white; margin-bottom: 10px;">
                <p style="margin: 0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase; text-align: center; padding: 3px;"">
                    ✅ Qtd. Greens
                </p>
                <h4 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-align: center; padding: 3px;"">
                    {m['total_green']} entry
                </h4>
                <p style="margin: 0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase; text-align: center; padding: 3px;"">
                    ❌ Qtd. Reds
                </p>
                <h4 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-align: center; padding: 3px;"">
                    {m['total_red']} entry
                </h4>
            </div>
            """,
            unsafe_allow_html=True,)
    

renderizar_cards_metricas_mercados(df_dados)

st.subheader("🔥 Recovery / Recuperação do Drawdown")
col_recovery, col_radar, col_vazio, col_vazio, col_vazio = st.columns([1.2, 1.17, .4, .4, .4])
with col_recovery:
    pico_banca = cd['pico_banca']
    dd_atual = banca_atual - pico_banca
    max_dd = cd.get("max_dd_reais", 0.0)
    recuperacao = max(0.0, min(100.0, (1 - (abs(dd_atual) / max_dd)) * 100))
    if dd_atual < 0:
        st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, #26163b 0%, #341c52 100%); padding: 5px; border-radius: 10px; color: white; margin-bottom: 10px;">
                        <h4 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-align: center; padding: 3px;"">
                            ↗️ Pico da Banca: <b>R$ {pico_banca:.2f}</b>
                        </h4>
                        <h4 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-align: center; padding: 3px;"">
                            🏦 Banca atual: <b>R$ {banca_atual:.2f}</b>
                        </h4>
                        <h4 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-align: center; padding: 3px;"">
                            💲DD atual: <b>{'R$ 0.00' if dd_atual >= 0 else f'-R$ {abs(dd_atual):.2f}'}</b>
                        </h4>
                        <h4 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-align: center; padding: 3px;"">
                            💸 Recuperação: {recuperacao:.1f}%
                        </h4>
                    </div>
                    """,
                    unsafe_allow_html=True,)
    else:
        st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%); padding: 4px; border-radius: 10px; color: white; margin-bottom: 10px;">
                        <h4 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-align: center; padding: 3px;"">
                            DD atual: {dd_atual:.2f}
                        </h4>
                        <h4 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: bold; text-align: center; padding: 3px;"">
                            Recuperação: 100% ✅"
                        </h4>
                    </div>
                    """,
                    unsafe_allow_html=True,)

with col_radar:
    radar_gestao(df_dados)