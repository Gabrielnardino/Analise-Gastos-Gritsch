# src/data_processing.py

import pandas as pd
import numpy as np
import os
import re
import streamlit as st

from src.db_connector import get_db_connection, get_raw_data

# --- DICIONÁRIOS E FUNÇÕES DE MAPEAMENTO (sem alterações) ---
mapa_regiao_correto = {
    'REFERÊNCIA SÃO PAULO': 'SUDESTE', 'Gritsch São Paulo (Perus)': 'SUDESTE', 'REFERÊNCIA RIBEIRAO PRETO': 'SUDESTE', 'GRITSCH - SAO (PERUS)': 'SUDESTE', 'GRITSCH - SAO (FREGUESIA)': 'SUDESTE', 'GRITSCH - MATRIZ': 'SUDESTE', 'Gritsch São Paulo (Freguesia)': 'SUDESTE',
    'REFERÊNCIA FOZ DO IGUAÇU': 'SUL', 'REFERÊNCIA CURITIBA': 'SUL', 'REFERÊNCIA MARINGÁ': 'SUL', 'Gritsch Curitiba Base': 'SUL', 'Gritsch Maringá': 'SUL', 'Gritsch Florianópolis': 'SUL', 'Gritsch Blumenau': 'SUL', 'Gritsch Cascavel': 'SUL', 'Gritsch Porto Alegre': 'SUL', 'Gritsch Chapecó': 'SUL', 'Gritsch Joinville': 'SUL', 'Gritsch Londrina': 'SUL', 'Gritsch Curitibanos': 'SUL', 'Gritsch Criciuma': 'SUL', 'Gritsch Pato Branco': 'SUL', 'Gritsch Laranjeiras do Sul': 'SUL', 'Gritsch Ponta Grossa': 'SUL', 'Gritsch Curitiba ECT': 'SUL', 'Gritsch Guarapuava': 'SUL', 'GRITSCH - PGR': 'SUL', 'GRITSCH - CWB (BASE)': 'SUL', 'GRITSCH - FLN': 'SUL', 'GRITSCH - BLN': 'SUL', 'GRITSCH - POA': 'SUL', 'GRITSCH - LDB': 'SUL', 'GRITSCH - CSC': 'SUL', 'GRITSCH - CWB (ECT)': 'SUL', 'GRITSCH - CHA': 'SUL', 'GRITSCH - CRI': 'SUL', 'GRITSCH - PBC': 'SUL', 'GRITSCH - CTB': 'SUL', 'GRITSCH - GPA': 'SUL', 'GRITSCH - MGA': 'SUL', 'GRITSCH - CWB (DIR)': 'SUL', 'GRITSCH - JOI': 'SUL',
    'REFERÊNCIA GOIÂNIA LOJA': 'CENTRO OESTE', 'REFERÊNCIA BRASILIA': 'CENTRO OESTE', 'REFERÊNCIA CUIABÁ LOJA': 'CENTRO OESTE', 'REFERÊNCIA SINOP': 'CENTRO OESTE', 'Gritsch Campo Grande': 'CENTRO OESTE', 'Gritsch Goiânia': 'CENTRO OESTE', 'Gritsch Brasília': 'CENTRO OESTE', 'Gritsch Rondonópolis': 'CENTRO OESTE', 'Gritsch Sinop': 'CENTRO OESTE', 'Gritsch Cuiabá': 'CENTRO OESTE', 'Gritsch Rio Verde': 'CENTRO OESTE', 'Gritsch Itumbiara': 'CENTRO OESTE', 'GRITSCH - ITR': 'CENTRO OESTE', 'GRITSCH - SNO': 'CENTRO OESTE', 'GRITSCH - RDN': 'CENTRO OESTE', 'GRITSCH - CBL': 'CENTRO OESTE', 'GRITSCH - GOI': 'CENTRO OESTE', 'GRITSCH - CGB': 'CENTRO OESTE', 'GRITSCH - CGR': 'CENTRO OESTE', 'GRITSCH - RVD': 'CENTRO OESTE', 'REFERÊNCIA GOIÂNIA AV RIO VERDE': 'CENTRO OESTE', 'GRITSCH - BSB': 'CENTRO OESTE',
    'REFERÊNCIA SALVADOR': 'NORDESTE', 'REFERÊNCIA LUIS EDUARDO MAGALHÃES': 'NORDESTE', 'REFERÊNCIA BALSAS': 'NORDESTE', 'Gritsch Salvador': 'NORDESTE', 'GRITSCH - SSA': 'NORDESTE',
    'REFERÊNCIA ARAGUAÍNA': 'NORTE', 'REFERÊNCIA VILHENA': 'NORTE', 'GRITSCH - PMW': 'NORTE',
}

def criar_mapa_padronizacao_naturezas():
    return {
        'LAVagem': '03.01 - LAVAGEM', 'LAVAGEM': '03.01 - LAVAGEM', '03.01 - LAVagem': '03.01 - LAVAGEM', 'MANUTENÇÃO DE VEÍCULOS': '03.03 - MANUTENÇÃO DE VEÍCULOS', 'DEDETIZAÇÃO DE VEÍCULO': '07.07 - DEDETIZAÇÃO DE VEÍCULO', 'COMBUSTÍVEL': '02.01 - COMBUSTÍVEL', 'IPVA (ANUAL)': '07.02 - IPVA (ANUAL)', 'ARLA': '02.02 - ARLA', 'TAXI': '16.01 - TAXI', 'ESTACIONAMENTO': 'ESTACIONAMENTO', 'MULTAS DE TRÂNSITO': 'MULTAS DE TRÂNSITO', 'LICENCIAMENTO': 'LICENCIAMENTO', 'CUSTAS': 'CUSTAS', 'SUBCONTRATAÇÃO DE TRANSPORTE': 'SUBCONTRATAÇÃO DE TRANSPORTE', 'SEGURO DE VEÍCULOS (FACULTATIVO)': 'SEGURO DE VEÍCULOS (FACULTATIVO)', 'PEDÁGIO': 'PEDÁGIO'
    }

def padronizar_naturezas(df):
    df_padronizado = df.copy()
    mapa = criar_mapa_padronizacao_naturezas()
    df_padronizado['Natureza_Correta'] = df_padronizado['Natureza_Correta'].replace(mapa)
    return df_padronizado

@st.cache_data(ttl=3600)
def get_processed_data():
    try:
        engine = get_db_connection()
        if engine is None: return pd.DataFrame(), pd.DataFrame()

        with open('sql/Fechamento FKM.sql', 'r', encoding='utf-8') as file:
            df_fechamento = get_raw_data(file.read(), engine)
        if df_fechamento.empty: return pd.DataFrame(), pd.DataFrame()

        df_fechamento['DataCriacao'] = pd.to_datetime(df_fechamento['DataCriacao'], errors='coerce')
        df_fechamento['Regiao'] = df_fechamento["FILIAL"].map(mapa_regiao_correto)
        df_fechamento['Regiao'].fillna('Regiao Nao definida', inplace=True)
        
        df_rateio = df_fechamento[df_fechamento['Regiao'] == 'Regiao Nao definida'].copy()
        df_sem_rateio = df_fechamento[df_fechamento['Regiao'] != 'Regiao Nao definida'].copy()

        df_sem_rateio['Natureza_Correta'].fillna(df_sem_rateio['NaturezaFinanceira'], inplace=True)
        df_padronizado = padronizar_naturezas(df_sem_rateio)

        df_final = df_padronizado.copy()
        df_final['empresa'] = df_final['FILIAL'].str.split().str[0]
        
        # --- ADIÇÃO DA COLUNA 'mes_ano' ---
        df_final['mes_ano'] = df_final['DataCriacao'].dt.strftime('%Y-%m')
        
        df_final.rename(columns={
            'DataCriacao': 'data', 'ValorTotal': 'valor', 'FILIAL': 'filial',
            'Regiao': 'regiao', 'Natureza_Correta': 'natureza_correta'
        }, inplace=True)

        colunas_app = ['data', 'valor', 'filial', 'regiao', 'natureza_correta', 'empresa', 'mes_ano']
        if not all(col in df_final.columns for col in colunas_app):
            st.error("Erro crítico: Colunas faltantes após o tratamento.")
            return pd.DataFrame(), pd.DataFrame()
        
        df_app = df_final[colunas_app].copy()
        df_app['valor'] = pd.to_numeric(df_app['valor'], errors='coerce').fillna(0)

        return df_app, df_rateio
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado durante o processamento dos dados: {e}")
        return pd.DataFrame(), pd.DataFrame()
