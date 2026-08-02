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
