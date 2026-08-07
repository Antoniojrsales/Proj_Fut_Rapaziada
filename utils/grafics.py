import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

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
        textposition="inside",
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

def grafico_evolucao_temporal(df: pd.DataFrame) -> None:
    """Renderiza a linha do tempo do Lucro Acumulado com Plotly."""
    if df is None or df.empty:
        st.warning("Sem dados para gerar o gráfico.")
        return

    # 1. Filtra apenas jogos concluídos
    df_finalizados = df[
        df["Resultado_Status"].isin(["Green", "Red"])
    ].copy()

    if df_finalizados.empty:
        st.warning("Não há jogos finalizados.")
        return

    # 2. Converte a data e agrupa o lucro total por dia
    df_finalizados["Data_Dia"] = pd.to_datetime(
        df_finalizados["Data"]
    ).dt.date
    df_diario = (
        df_finalizados.groupby("Data_Dia")
        .agg(Lucro_Diario=("Lucro_R$", "sum"))
        .reset_index()
    )

    # 3. Calcula a evolução do Lucro ACUMULADO dia a dia
    df_diario = df_diario.sort_values(by="Data_Dia").reset_index(drop=True)
    df_diario["Lucro_Acumulado"] = df_diario["Lucro_Diario"].cumsum()
    df_diario["Data_Str"] = pd.to_datetime(df_diario["Data_Dia"]).dt.strftime(
        "%d/%m/%Y"
    )

    # 4. Define as cores dinâmicas com base no SALDO FINAL ACUMULADO
    ultimo_lucro = df_diario["Lucro_Acumulado"].iloc[-1]
    cor_linha = "#00C04D" if ultimo_lucro >= 0 else "#FF4B4B"
    cor_preenchimento = (
        "rgba(0, 192, 77, 0.1)"
        if ultimo_lucro >= 0
        else "rgba(255, 75, 75, 0.15)"
    )

    # 5. Renderiza o Gráfico com o Lucro Acumulado no eixo Y
    fig = px.line(
        df_diario,
        x="Data_Str",
        y="Lucro_Acumulado",
        markers=True,
        text=df_diario["Lucro_Acumulado"].apply(lambda x: f"R$ {x:.2f}"),
    )

    # 6. Atualiza Traços
    fig.update_traces(
        mode="lines+markers+text",
        line=dict(color=cor_linha, width=3, shape="spline"),
        marker=dict(size=6, color=cor_linha),
        fill="tozeroy",
        fillcolor=cor_preenchimento,
        hovertemplate="<b>Data:</b> %{x}<br><b>Lucro Acumulado:</b> R$ %{y:.2f}<extra></extra>",
        textposition="top center",
        cliponaxis=False,
        textfont=dict(family="Arial", size=12, color="black"),
    )

    # 7. Layout e Navegação
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis_title="Data",
        yaxis_title="Lucro Acumulado (R$)",
        height=400,
        margin=dict(t=30, b=40, l=60, r=80),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(200, 200, 200, 0.2)",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(200, 200, 200, 0.2)",
            tickprefix="R$ ",
            tickformat=",.2f",
            autorange=True,
            fixedrange=False,
        ),
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": True, "scrollZoom": True},
    )
