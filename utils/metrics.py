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
        "ranking_mercados": lista_ranking
    }

def grafico_rank_mercados(df: pd.DataFrame) -> None:
    """Filtra os dados finalizados, agrupa por mercado e renderiza o gráfico de ranking com Plotly."""
    if df is None or df.empty:
        st.warning("Sem dados para gerar o gráfico.")
        return

    # 1. Filtra apenas jogos concluídos
    df_finalizados = df[
        df["Resultado_Status"].isin(["Green", "Red"])
    ].copy()

    if df_finalizados.empty:
        st.warning("Não há jogos finalizados para o ranking.")
        return

    # 2. Agrupa e ordena
    ranking = (
        df_finalizados.groupby("Mercado")
        .agg(Lucro_Total=("Lucro_R$", "sum"), Total_Jogos=("Stake", "count"))
        .reset_index()
    )

    ranking = ranking.sort_values(by="Lucro_Total", ascending=True).reset_index(
        drop=True
    )
    ranking["Cor"] = ranking["Lucro_Total"].apply(
        lambda x: "Green" if x >= 0 else "Red"
    )

    # 3. Renderiza o Plotly
    fig = px.bar(
        ranking,
        x="Lucro_Total",
        y="Mercado",
        title="<b>Ranking de Mercados por Lucro Líquido</b>",
        orientation="h",
        text=ranking["Lucro_Total"].apply(lambda x: f"R$ {x:.2f}"),
        color="Cor",
        color_discrete_map={"Green": "#00C04D", "Red": "#FF4B4B"},
    )

    fig.update_traces(
        textfont=dict(weight="bold", family="Arial", color="black", size=14),
        textposition="outside",
        texttemplate="R$ %{x:.2f}",
        cliponaxis=False  
    )

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.36, 
        title_font_size=22, 
        showlegend=False,
        xaxis_title="Lucro Líquido (R$)",
        yaxis_title="",
        height=400,
        margin=dict(t=40, b=10, l=140, r=80),
        xaxis=dict(
            tickprefix="R$ ",
            tickformat=",",
            
            ),
        yaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=1
        )
    )

    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

def grafico_contagem_mercados(df: pd.DataFrame) -> None:
    """Renderiza um gráfico de contagem de mercados com Plotly."""
    if df is None or df.empty:
        st.warning("Sem dados para gerar o gráfico.")
        return

    # 1. Filtra apenas jogos concluídos
    df_finalizados = df[df["Resultado_Status"].isin(["Green", "Red"])].copy()

    if df_finalizados.empty:
        st.warning("Não há jogos finalizados para o ranking.")
        return

    # 2. Agrupa e ordena
    contagem = (df_finalizados.groupby("Resultado_Status").agg(Total_Jogos=("Stake", "count")).reset_index())

    # 3. Renderiza o Plotly
    fig = px.pie(
        contagem,
        values="Total_Jogos",
        names="Resultado_Status",
        title="<b>Taxa de Acerto (Green vs Red)</b>",
        color="Resultado_Status",
        color_discrete_map={"Green": "#00C04D", "Red": "#FF4B4B"},
    )

    # 4. Ajustes finos do rótulo e layout
    fig.update_traces(
        textfont=dict(weight="bold", family="Arial", color="black", size=14),
        textinfo="percent",  # Exibe a contagem absoluta e a porcentagem
        textposition="outside",  # Evita sobreposição na fatia pequena de Red
        pull=[0, 0.05],  # Destaca ligeiramente a fatia de Red
    )

    fig.update_layout(
        title_x=0.36, 
        title_font_size=22, 
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
        height=400,
        margin=dict(t=60, b=60, l=20, r=20),
    )

    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})