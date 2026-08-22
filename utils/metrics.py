import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
import plotly.express as px

def metricas_gerais(df: pd.DataFrame) -> dict:
    """
    Calcula métricas gerais a partir do DataFrame processado.
    Retorna um dicionário padronizado com os dados para renderização.
    """
    # Estrutura base padrão para evitar KeyError na interface
    base_metrics = {
        "total_green": 0,
        "total_red": 0,
        "total_jogos": 0,
        "taxa_acerto": 0.0,
        "total_greens_rs": 0.0,
        "total_reds_rs": 0.0,
        "lucro_total": 0.0,
        "lucro_acumulado": 0.0,
        "total_pendentes": 0,
        "ranking_mercados": [],
        "porcentagem_banca": 0.0,
        "media_over0.5": 0.0,
    }

    if df is None or df.empty:
        return base_metrics

    # Considera apenas partidas finalizadas (evita jogos pendentes nas contagens)
    df_green = df[df['Resultado_Status'] == 'Green']
    df_red = df[df['Resultado_Status'] == 'Red']
    df_finalizados = df[df['Resultado_Status'].isin(['Green', 'Red'])]
    df_pendentes = df[df['Resultado_Status'] == 'Pendente']
    df_investimento = float(df_finalizados['Stake'].sum()) if not df_finalizados.empty else 0.0

    total_green = len(df_green)
    total_red = len(df_red)
    total_jogos = total_green + total_red
    total_pendentes = len(df_pendentes)

    taxa_acerto = (total_green / total_jogos * 100) if total_jogos > 0 else 0.0

    total_greens_rs = float(df_green['Lucro_R$'].sum()) if not df_green.empty else 0.0
    total_reds_rs = float(df_red['Lucro_R$'].sum()) if not df_red.empty else 0.0
    
    # Soma total apurada nos jogos finalizados
    lucro_total = float(df['Lucro_R$'].sum())
    
    # Resgata o último acumulado se a coluna existir, senão usa o lucro_total
    lucro_acumulado = float(df['Lucro_Acumulado'].iloc[-1]) if 'Lucro_Acumulado' in df.columns and not df['Lucro_Acumulado'].empty else lucro_total

    roi = (lucro_total / df_investimento * 100) if df_investimento > 0 else 0.0

    # 3. Agrupamento do Ranking (Sintaxe segura para renomear direto)
    if not df_finalizados.empty:
        ranking = (df_finalizados.groupby("Mercado").agg(Lucro_Total=("Lucro_R$", "sum"), Total_Jogos=("Stake", "count")).reset_index())

        # Ordena pelo maior Lucro
        ranking = ranking.sort_values(by="Lucro_Total", ascending=False).reset_index(drop=True)

        # Percentual do Lucro
        total_lucro_ranking = ranking["Lucro_Total"].sum()
        ranking["Percentual"] = ((ranking["Lucro_Total"] / total_lucro_ranking * 100).round(2)
                                    if total_lucro_ranking > 0
                                    else 0.0
                                )

        lista_ranking = ranking.to_dict(orient="records")
    else:
        lista_ranking = []

    # 1. Valor base onde o projeto começou
    BANCA_INICIAL_BASE = 110.0

    # 4. Porcentagem exata sobre a banca inicial
    porcentagem_banca = ((lucro_total / BANCA_INICIAL_BASE) * 100 if BANCA_INICIAL_BASE > 0 else 0.0
    )

    media_over05 = df_finalizados[df_finalizados['Mercado'] == 'Over0.5_3porc'].groupby('Stake')['Stake'].sum().mean()

    return {
        "total_green": total_green,
        "total_red": total_red,
        "total_jogos": total_jogos,
        "taxa_acerto": taxa_acerto,
        "total_greens_rs": total_greens_rs,
        "total_reds_rs": total_reds_rs,
        "lucro_total": lucro_total,
        "lucro_acumulado": lucro_acumulado,
        "total_pendentes": total_pendentes,
        "investimento_total": df_investimento,
        "roi": roi,
        "ranking_mercados": lista_ranking,
        "porcentagem_banca": porcentagem_banca,
        "media_over0.5": media_over05,
    }

def media_por_mercados(df: pd.DataFrame) -> dict:
    """Calcula ROI, Lucro, Stake Média, Drawdown e Sequências agrupados por mercado."""
    if df is None or df.empty:
        return {}

    # 1. Filtra apenas jogos finalizados
    df_finalizados = df[
        df["Resultado_Status"].isin(["Green", "Red"])
    ].copy()

    if df_finalizados.empty:
        return {}

    col_data = (
        "Data" if "Data" in df_finalizados.columns else df_finalizados.columns[0]
    )
    col_stake = "Stake_R$" if "Stake_R$" in df_finalizados.columns else "Stake"

    metricas_mercados = {}

    # Itera por mercado calculando métricas financeiras e curva de risco/drawdown
    for mercado, grupo in df_finalizados.groupby("Mercado"):
        # Garante ordenação cronológica para o Drawdown
        grupo_ord = grupo.sort_values(by=col_data).copy()

        invest = float(grupo_ord[col_stake].sum())
        lucro = float(grupo_ord["Lucro_R$"].sum())
        total_jogos = len(grupo_ord)
        stake_med = (
            float(grupo_ord[col_stake].mean()) if total_jogos > 0 else 0.0
        )
        roi = float((lucro / invest * 100) if invest > 0 else 0.0)

        # Curva de Drawdown
        lucro_acumulado = grupo_ord["Lucro_R$"].cumsum()
        pico_historico = lucro_acumulado.cummax()
        drawdown_r = lucro_acumulado - pico_historico
        max_dd_reais = abs(
            float(drawdown_r.min())
        )  # Valor absoluto do maior fundo

        # Sequência contínua de jogos em Drawdown (Recuperação)
        em_dd = (drawdown_r < 0).astype(int)
        grupos_dd = (em_dd != em_dd.shift()).cumsum() * em_dd
        jogos_em_dd = (
            int(grupos_dd.value_counts().drop(0, errors="ignore").max())
            if (em_dd == 1).any()
            else 0
        )

        # Sequência máxima de Reds Consecutivos
        is_red = (grupo_ord["Resultado_Status"] == "Red").astype(int)
        grupos_red = (is_red != is_red.shift()).cumsum() * is_red
        max_reds = (
            int(grupos_red.value_counts().drop(0, errors="ignore").max())
            if (is_red == 1).any()
            else 0
        )

        metricas_mercados[mercado] = {
            "jogos": total_jogos,
            "investimento": invest,
            "lucro": lucro,
            "stake_media": stake_med,
            "roi": roi,
            "max_dd_reais": max_dd_reais,
            "jogos_em_dd": jogos_em_dd,
            "max_reds": max_reds,
        }

    return metricas_mercados

def renderizar_cards_metricas_mercados(df: pd.DataFrame) -> None:
    """Renderiza os cards visuais fiéis à sugestão da imagem."""
    dados_mercados = media_por_mercados(df)

    if not dados_mercados:
        st.info("Nenhum dado consolidado por mercado para exibir.")
        return

    colunas = st.columns(len(dados_mercados))

    for col, (mercado, dados) in zip(colunas, dados_mercados.items()):
        roi_val = dados["roi"]
        lucro_val = dados["lucro"]

        with col:
            st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, #202d47 0%, #273b5c 100%); padding: 8px; border-radius: 10px; color: white; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span style="font-weight: 700; font-size: 1.2rem; text-transform: uppercase;">
                                📊 {mercado}
                            </span>
                            <span style="font-size: 0.9rem; font-weight: 700; padding: 2px 8px; border-radius: 6px;">
                                Max DD: -R$ {dados['max_dd_reais']:.2f}
                            </span>
                        </div>
                        <div style="font-size: 1rem; font-weight: 800; line-height: 1.2; margin-bottom: 10px;">
                            🎯ROI: {roi_val:+.2f}%
                        </div>
                        <div style="border-top: 1px solid #f1f5f9; padding-top: 8px; font-size: 0.9rem; display: flex; justify-content: space-between;">
                            <span>💸Lucro: <b>R$ {lucro_val:.2f}</b></span>
                            <span>💸Stake Méd.: <b>R$ {dados['stake_media']:.2f}</b></span>
                        </div>
                        <div style="padding-top: 5px; font-size: 0.9rem; display: flex; justify-content: space-between;">
                            <span>Max Reds Seguidos: <b>{dados['max_reds']}</b></span>
                            <span>Jogos em DD: <b>{dados['jogos_em_dd']}</b></span>
                        </div>    
                        <div style="margin-top: 10px; padding-top: 4px; border-top: 1px dashed #f1f5f9; font-size: 0.9rem; text-align: right;">
                            {dados['jogos']} jogos analisados
                        </div>                        
                    </div>
                    """,
                    unsafe_allow_html=True,)

def calcular_drawdown(df: pd.DataFrame, 
                      coluna_lucro: str = "Lucro_R$", 
                      coluna_data: str = "Data",
                      banca_inicial: float = 110.0) -> dict:
    """Calcula métricas de Drawdown Histórico (Máximo) e Drawdown Atual (Momento Presente).

    Funciona tanto para o DataFrame geral quanto para um mercado filtrado.
    """
    padrao = {
        "max_dd_reais": 0.0,
        "max_dd_perc_banca": 0.0,
        "pico_banca": banca_inicial,
        "pico_lucro": 0.0,
        "dd_atual_reais": 0.0,
        "dd_atual_perc_banca": 0.0,
        "dd_atual_perc_lucro": 0.0,
        "em_dd_agora": False,
        "jogos_em_dd": 0,
        "max_reds_seguidos": 0,
    }

    if df is None or df.empty:
        return padrao

    # 1. Filtra apenas jogos finalizados
    df_finalizados = df[df["Resultado_Status"].isin(["Green", "Red"])].copy()

    if df_finalizados.empty:
        return padrao

    # 2. Garante ordenação cronológica
    if coluna_data in df_finalizados.columns:
        df_ord = df_finalizados.sort_values(by=coluna_data).copy()
    else:
        df_ord = df_finalizados.copy()

    # 3. Curva Acumulada e Picos Históricos
    serie_acumulada = df_ord[coluna_lucro].cumsum()
    picos_lucro = serie_acumulada.cummax()
    curva_dd = serie_acumulada - picos_lucro

    # === DRAWDOWN HISTÓRICO MÁXIMO ===
    max_dd_reais = abs(float(curva_dd.min()))
    pico_lucro_max = float(picos_lucro.max())
    pico_banca_max = float(banca_inicial + pico_lucro_max)
    max_dd_perc_banca = (float((max_dd_reais / pico_banca_max) * 100) if pico_banca_max > 0 else 0.0)

    # === DRAWDOWN ATUAL (MOMENTO PRESENTE) 👉 NOVO BLOCO ===
    ultimo_lucro = float(serie_acumulada.iloc[-1])
    ultimo_pico_lucro = float(picos_lucro.iloc[-1])
    ultimo_pico_banca = float(banca_inicial + ultimo_pico_lucro)
    dd_atual_reais = abs(float(ultimo_lucro - ultimo_pico_lucro))

    # % Sobre o Pico da Banca Total (Conforme sugerido na Imagem 1)
    dd_atual_perc_banca = (float((dd_atual_reais / ultimo_pico_banca) * 100) if ultimo_pico_banca > 0 else 0.0)

    # % Sobre o Lucro Histórico
    dd_atual_perc_lucro = (float((dd_atual_reais / ultimo_pico_lucro) * 100) if ultimo_pico_lucro > 0  else 0.0)

    em_dd_agora = dd_atual_reais > 0

    # 4. Sequência Máxima de Jogos em Drawdown Contínuo
    em_dd = (curva_dd < 0).astype(int)
    grupos_dd = (em_dd != em_dd.shift()).cumsum() * em_dd
    jogos_em_dd = ( int(grupos_dd.value_counts().drop(0, errors="ignore").max())
                    if (em_dd == 1).any()
                    else 0)

    # 5. Sequência Máxima de Reds Consecutivos
    col_status = ("Resultado_Status" if "Resultado_Status" in df_ord.columns else "Resultado")
    is_red = (df_ord[col_status] == "Red").astype(int)
    grupos_red = (is_red != is_red.shift()).cumsum() * is_red
    max_reds = ( int(grupos_red.value_counts().drop(0, errors="ignore").max())
                if (is_red == 1).any()
                else 0)

    return {
       "max_dd_reais": max_dd_reais,
        "max_dd_perc_banca": max_dd_perc_banca,
        "pico_banca": ultimo_pico_banca,
        "pico_lucro": ultimo_pico_lucro,
        "dd_atual_reais": dd_atual_reais,
        "dd_atual_perc_banca": dd_atual_perc_banca,  # 👈 Usar este no card
        "dd_atual_perc_lucro": dd_atual_perc_lucro,
        "em_dd_agora": em_dd_agora,
        "jogos_em_dd": jogos_em_dd,
        "max_reds_seguidos": max_reds,
    }