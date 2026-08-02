#-- 📚 Bibliotecas --#
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa, converte tipos e adiciona colunas analíticas (Gols, Green/Red/Pendente, Lucro e Lucro Acumulado).
    """
    if df.empty:
        return df

    # Faz uma cópia para evitar avisos de SettingWithCopyWarning do Pandas
    df = df.copy()

    # =========================================================
    # 1. LIMPEZA E CONVERSÃO DE TIPOS
    # =========================================================

    # A. Coluna 'Mercado'
    if 'Mercado' in df.columns:
        df['Mercado'] = df['Mercado'].astype(str).str.strip()

    # B. Coluna 'Stake'
    if 'Stake' in df.columns:
        df['Stake'] = (
            df['Stake']
            .astype(str)
            .str.replace('R$', '', regex=False)
            .str.strip()
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
        )
        df['Stake'] = df['Stake'].str.replace(r'[^\d.]+', '', regex=True)
        df['Stake'] = pd.to_numeric(df['Stake'], errors='coerce').fillna(0.0)
    else:
        df['Stake'] = 0.0

    # C. Coluna 'Data' e 'Mes/Ano'
    if 'Data' in df.columns:
        # Suporta formatos DD/MM e DD/MM/YYYY sem descartar linhas
        df['Data_Parsed'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce').fillna(
            pd.to_datetime(df['Data'], format='%d/%m', errors='coerce')
        )
        
        df = df.dropna(subset=['Data_Parsed']).copy()

        ano_atual = datetime.now().year
        df['Data'] = df['Data_Parsed'].apply(lambda d: d.replace(year=ano_atual) if d.year == 1900 else d)
        df.drop(columns=['Data_Parsed'], inplace=True, errors='ignore')

        # Ordena por data para que o lucro acumulado respeite a linha do tempo
        df = df.sort_values('Data').reset_index(drop=True)
        df['Mes/Ano'] = df['Data'].dt.strftime('%b/%Y')

    # D. Coluna 'Odd %'
    if 'Odd %' in df.columns:
        df['Odd %'] = df['Odd %'].astype(str).str.replace(',', '.', regex=False)
        df['Odd %'] = pd.to_numeric(df['Odd %'], errors='coerce').fillna(0.0)
    else:
        df['Odd %'] = 0.0

    # =========================================================
    # 2. ADIÇÃO DE COLUNAS ANALÍTICAS (MÉTRICAS & PLACAR)
    # =========================================================

    # Garantia contra KeyError caso as colunas de time/placar faltem
    for col in ['X_Ks', 'X_Fora']:
        if col not in df.columns:
            df[col] = ""

    # Converte placares para número, mantendo células vazias/espaços como NaN
    df['X_Ks_num'] = pd.to_numeric(df['X_Ks'].astype(str).str.strip(), errors='coerce')
    df['X_Fora_num'] = pd.to_numeric(df['X_Fora'].astype(str).str.strip(), errors='coerce')

    # Identifica se a partida REALMENTE tem o placar preenchido
    tem_placar = df['X_Ks_num'].notna() & df['X_Fora_num'].notna()

    # Format visual: exibe o inteiro se preenchido, ou string vazia "" se pendente
    df['X_Ks'] = np.where(tem_placar, df['X_Ks_num'].astype('Int64').astype(str), "")
    df['X_Fora'] = np.where(tem_placar, df['X_Fora_num'].astype('Int64').astype(str), "")

    # ⚽ Total de Gols (Apenas para partidas com placar)
    df['Gols'] = np.where(tem_placar, df['X_Ks_num'] + df['X_Fora_num'], np.nan)

    # 🎯 Regras de Negócio: Status (Green / Red / Pendente)
    cond_over = (df['Mercado'] == 'Over0.5_3porc') & (df['Gols'] > 0)
    cond_under = (df['Mercado'] == 'Under6.5_3porc') & (df['Gols'] <= 6)

    df['Resultado_Status'] = np.where(
        ~tem_placar, 
        'Pendente', 
        np.where(cond_over | cond_under, 'Green', 'Red')
    )

    # 💰 Calculo do Lucro / Prejuízo Líquido (R$)
    lucro_green = df['Stake'] * (df['Odd %'] / 100)
    prejuizo_red = -df['Stake']

    df['Lucro_R$'] = np.where(
        df['Resultado_Status'] == 'Pendente',
        0.0,
        np.where(df['Resultado_Status'] == 'Green', lucro_green, prejuizo_red)
    )

    # 📈 Lucro Acumulado
    df['Lucro_Acumulado'] = df['Lucro_R$'].cumsum()

    # Limpeza de colunas temporárias
    df.drop(columns=['X_Ks_num', 'X_Fora_num'], inplace=True, errors='ignore')

    return df

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
        "total_pendentes": 0
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
        "roi": roi
    }
