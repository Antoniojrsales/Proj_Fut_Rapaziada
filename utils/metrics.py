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
    BANCA_INICIAL_BASE = 100.0

    # 4. Porcentagem exata sobre a banca inicial
    porcentagem_banca = (
        (lucro_total / BANCA_INICIAL_BASE) * 100
        if BANCA_INICIAL_BASE > 0
        else 0.0
    )

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
        "porcentagem_banca": porcentagem_banca
    }

