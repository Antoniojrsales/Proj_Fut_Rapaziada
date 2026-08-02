#-- 📚 Bibliotecas --#
import pandas as pd
import numpy as np
from datetime import datetime

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa, converte tipos e adiciona colunas analíticas (Gols, Green/Red, Lucro e Lucro Acumulado).
    """
    if df.empty:
        return df

    # Faz uma cópia para evitar avisos do Pandas
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

    # C. Coluna 'Data' e 'Mes/Ano'
    if 'Data' in df.columns:
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m', errors='coerce')
        df = df.dropna(subset=['Data']).copy()

        ano_atual = datetime.now().year
        df['Data'] = df['Data'].apply(lambda d: d.replace(year=ano_atual) if d.year == 1900 else d)
        
        # Ordena por data para que o lucro acumulado fique correto
        df = df.sort_values('Data').reset_index(drop=True)
        df['Mes/Ano'] = df['Data'].dt.strftime('%b/%Y')

    # D. Colunas Numéricas (Odd %, X_Ks, X_Fora)
    cols_numericas = ['Odd %', 'X_Ks', 'X_Fora']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # =========================================================
    # 2. ADIÇÃO DE COLUNAS ANALÍTICAS (MÉTRICAS)
    # =========================================================

    # ⚽ Total de Gols
    if 'X_Ks' in df.columns and 'X_Fora' in df.columns:
        df['Gols'] = df['X_Ks'] + df['X_Fora']
    else:
        df['Gols'] = 0

    # 🎯 Regras de Negócio: Definição de Green / Red
    cond_over = (df['Mercado'] == 'Over0.5_3porc') & (df['Gols'] > 0)
    cond_under = (df['Mercado'] == 'Under6.5_3porc') & (df['Gols'] <= 6) # Correção: <= 6

    # Aplica 'Green' se atender a qualquer uma das condições, senão 'Red'
    df['Resultado_Status'] = np.where(cond_over | cond_under, 'Green', 'Red')

    # 💰 Calculo do Lucro / Prejuízo Líquido (R$)
    # Se Green: Stake * (Odd % / 100) | Se Red: -Stake
    lucro_green = df['Stake'] * (df['Odd %'] / 100)
    prejuizo_red = -df['Stake']

    df['Lucro_R$'] = np.where(df['Resultado_Status'] == 'Green', lucro_green, prejuizo_red)

    # 📈 Lucro Acumulado (Para gráficos de evolução da banca)
    df['Lucro_Acumulado'] = df['Lucro_R$'].cumsum()

    return df