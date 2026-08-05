import pandas as pd
import numpy as np
import re

def processar_regras_lay(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processa e valida automaticamente se o placar do Lay bateu com o placar real.
    Gera o status (Green/Red) e o Lucro real da entrada.
    """
    # 1. Garante que os valores em Lay_placar sejam tratados como string limpa
    df['Lay_placar_clean'] = df['Lay_placar'].fillna('').astype(str).str.strip().str.lower()
    
    def validar_linha(row):
        placar_lay = str(row.get('Lay_placar', '')).strip().lower()
        
        status_atual = row.get('Resultado_Status', '')
        lucro_atual = row.get('Lucro_R$', 0.0)
        
        # Se a coluna Lay_placar estiver VAZIA, 'nan' ou nula, mantemos o cálculo original
        if not placar_lay or placar_lay in ['nan', 'none', '']:
            return status_atual, lucro_atual
        
        try:
            # Garante a conversão segura de X_Ks e X_Fora (se for vazio/NaN vira 0)
            x_ks_raw = str(row.get('X_Ks', '')).strip()
            x_fora_raw = str(row.get('X_Fora', '')).strip()
            
            if not x_ks_raw or x_ks_raw.lower() in ['nan', 'none'] or not x_fora_raw or x_fora_raw.lower() in ['nan', 'none']:
                return status_atual, lucro_atual

            gols_reais_casa = int(float(x_ks_raw))
            gols_reais_fora = int(float(x_fora_raw))
            
            # Extrai os números do placar apostado (ex: "1x2" -> 1 e 2)
            gols_apostados = re.findall(r'\d+', placar_lay)
            
            if len(gols_apostados) == 2:
                gols_apostados_casa = int(gols_apostados[0])
                gols_apostados_fora = int(gols_apostados[1])
                
                # Pega o valor da Stake com tratamento para nulos
                stake_val = str(row.get('Stake', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                stake_float = float(stake_val) if stake_val else 0.0
                
                # SE O PLACAR REAL FOR EQUIVALENTE AO APOSTADO -> RED
                if (gols_reais_casa == gols_apostados_casa) and (gols_reais_fora == gols_apostados_fora):
                    return 'Red', -stake_float
                # SE FOR DIFERENTE -> GREEN (+R$ 1,00)
                else:
                    return 'Green', 1.00

        except Exception as e:
            print(f"Erro ao processar linha de Lay: {e}")
            return status_atual, lucro_atual

        return status_atual, lucro_atual

    # Aplica a função linha por linha no DataFrame
    resultados = df.apply(validar_linha, axis=1)
    
    # Atualiza as colunas de status e lucro
    df['Resultado_Status'] = [r[0] for r in resultados]
    df['Lucro_R$'] = [r[1] for r in resultados]
    
    # Remove a coluna temporária de limpeza
    df.drop(columns=['Lay_placar_clean'], inplace=True, errors='ignore')
    
    return df
