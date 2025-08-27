# pages/1_Manutencao.py (ou o arquivo que você preferir)

import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

# Importar as funções do nosso conector
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.db_connector import get_db_connection, get_raw_data

# --- Configuração da Página ---
st.set_page_config(
    page_title="Análise de Custos",
    page_icon="📊",
    layout="wide"
)

# --- Função de Carregamento e Tratamento de Dados (sem alterações) ---
@st.cache_data
def carregar_dados_manutencao():
    print("Executando carregar_dados_manutencao()...")
    engine = get_db_connection()
    if not engine:
        st.error("Falha na conexão com o banco de dados.")
        return pd.DataFrame()

    try:
        with open('sql/Fechamento FKM.sql', 'r', encoding='utf-8') as file:
            query = file.read()
        df = get_raw_data(query, engine)
    except Exception as e:
        st.error(f"Ocorreu um erro ao buscar os dados: {e}")
        return pd.DataFrame()

    # Tratamento de Dados
    df['DataCriacao'] = pd.to_datetime(df['DataCriacao'], errors='coerce')
    df['Mes/Ano'] = df['DataCriacao'].dt.to_period('M')
    df['ValorTotal'] = df['ValorTotal'].fillna(0)

    mapa_regiao = {
        'Gritsch Curitiba Base': 'SUL', 'Gritsch Maringá': 'SUL', 'Gritsch Florianópolis': 'SUL',
        'Gritsch Campo Grande': 'CENTRO OESTE', 'Gritsch Blumenau': 'SUL', 'Gritsch Cascavel': 'SUL',
        'Gritsch Porto Alegre': 'SUL', 'Gritsch São Paulo (Perus)': 'SUDESTE', 'Gritsch Goiânia': 'CENTRO OESTE',
        'Gritsch Brasília': 'CENTRO OESTE', 'Gritsch Rondonópolis': 'CENTRO OESTE', 'Gritsch São Paulo (Freguesia)': 'SUDESTE',
        'Gritsch Chapecó': 'SUL', 'Gritsch Joinville': 'SUL', 'Gritsch Londrina': 'SUL',
        'Gritsch Curitibanos': 'SUL', 'Gritsch Criciuma': 'SUL', 'Gritsch Sinop': 'CENTRO OESTE',
        'Gritsch Pato Branco': 'SUL', 'Gritsch Cuiabá': 'CENTRO OESTE', 'Gritsch Rio Verde': 'CENTRO OESTE',
        'Gritsch Laranjeiras do Sul': 'SUL', 'Gritsch Itumbiara': 'CENTRO OESTE', 'Gritsch Ponta Grossa': 'SUL',
        'Gritsch Curitiba ECT': 'SUL', 'Gritsch Salvador': 'NORDESTE', 'Gritsch Guarapuava': 'SUL', 'Gritsch Palmas': 'NORTE'
    }
    df['Regiao'] = df['FILIAL'].map(mapa_regiao)
    df['Regiao'].fillna('Regiao Nao definida', inplace=True)

    conditions = [
        (df['FILIAL'].str.contains('GRITSCH', case=False, na=False)),
        (df['FILIAL'].str.contains('REFERÊNCIA', case=False, na=False)),
        (df['FILIAL'].str.contains('RATEIO', case=False, na=False)),
    ]
    choices = ['Gritsch', 'Referência', 'Rateio']
    df['Empresa'] = np.select(conditions, choices, default='Outro')

    return df

# --- Layout Principal ---
st.title("📊 Dashboard de Análise de Custos")

# Carregar os dados
df_completo = carregar_dados_manutencao()

if df_completo.empty:
    st.warning("Não foi possível carregar os dados.")
else:
    # --- Criação das Abas Superiores ---
    tab_manutencao, tab_estoque, tab_outra_analise = st.tabs([
        "Visão Geral de Manutenção", 
        "Análise de Estoque (Em Breve)", 
        "Outra Análise (Em Breve)"
    ])

    # --- Conteúdo da Aba de Manutenção ---
    with tab_manutencao:
        st.header("Análise Detalhada dos Custos de Manutenção")

        # Colocar os filtros dentro de colunas para organizar o layout
        col1, col2, col3 = st.columns([0.25, 0.25, 0.5]) # Ajuste as proporções conforme necessário

        with col1:
            empresa_selecionada = st.selectbox(
                "Selecione a Empresa:",
                options=['Todas'] + sorted(df_completo['Empresa'].unique()),
                index=0
            )
        
        with col2:
            # Exemplo de outro filtro que você pode adicionar
            regiao_selecionada = st.selectbox(
                "Selecione a Região:",
                options=['Todas'] + sorted(df_completo['Regiao'].unique()),
                index=0
            )

        # Aplicar filtros
        df_filtrado = df_completo.copy()
        if empresa_selecionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Empresa'] == empresa_selecionada]
        if regiao_selecionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Regiao'] == regiao_selecionada]

        st.markdown("---")

        # Exibir Análises
        st.subheader(f"Exibindo dados para: {empresa_selecionada} | Região: {regiao_selecionada}")

        custo_mensal = df_filtrado.groupby(df_filtrado['Mes/Ano'].astype(str))['ValorTotal'].sum().reset_index()
        
        fig_custo_mensal = px.bar(
            custo_mensal,
            x='Mes/Ano',
            y='ValorTotal',
            title=f"Custo Mensal de Manutenção",
            labels={'Mes/Ano': 'Mês/Ano', 'ValorTotal': 'Custo Total (R$)'},
            text_auto='.2s'
        )
        st.plotly_chart(fig_custo_mensal, use_container_width=True)

    # --- Conteúdo da Aba de Estoque ---
    with tab_estoque:
        st.header("Análise de Estoque")
        st.info("Esta seção está em desenvolvimento.")
        # Aqui você adicionaria a lógica para a análise de estoque no futuro

    # --- Conteúdo da Terceira Aba ---
    with tab_outra_analise:
        st.header("Outra Análise")
        st.info("Esta seção está em desenvolvimento.")

