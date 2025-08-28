# app.py (Versão com Navegação Superior)

import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from streamlit_option_menu import option_menu
from src.db_connector import get_db_connection, get_raw_data


st.set_page_config(page_title="Dashboard Grupo Gritsch", layout="wide")

@st.cache_data
def carregar_dados_manutencao():
    # (O código desta função é o mesmo que já tínhamos, sem alterações)
    print("Executando carregar_dados_manutencao()...")
    engine = get_db_connection()
    if not engine: return pd.DataFrame()
    try:
        with open('sql/Fechamento FKM.sql', 'r', encoding='utf-8') as file:
            query = file.read()
        df = get_raw_data(query, engine)
    except Exception as e:
        st.error(f"Ocorreu um erro ao buscar os dados: {e}")
        return pd.DataFrame()
    
    
    
    
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
    df['Regiao']= df['Regiao'].fillna('Regiao Nao definida')
    
    conditions = [
        (df['FILIAL'].str.contains('GRITSCH', case=False, na=False)),
        (df['FILIAL'].str.contains('REFERÊNCIA', case=False, na=False)),
        (df['FILIAL'].str.contains('RATEIO', case=False, na=False)),
    ]
    choices = ['Gritsch', 'Referência', 'Rateio']
    df['Empresa'] = np.select(conditions, choices, default='Verificar')
    
    return df





# --- FUNÇÕES QUE REPRESENTAM CADA PÁGINA ---
def pagina_manutencao():
    st.title("🔧 Análise de Custos de Manutenção")
    df_manutencao = carregar_dados_manutencao()

    if df_manutencao.empty:
        st.warning("Não foi possível carregar os dados de manutenção.")
        return

    # Filtros
    col1, col2, col3 = st.columns([0.25, 0.25, 0.5])
    with col1:
        empresa = st.selectbox("Empresa", options=['Todas'] + sorted(df_manutencao['Empresa'].unique()))
    with col2:
        regiao = st.selectbox("Região", options=['Todas'] + sorted(df_manutencao['Regiao'].unique()))

    # Lógica de filtragem
    df_filtrado = df_manutencao.copy()
    if empresa != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Empresa'] == empresa]
    if regiao != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Regiao'] == regiao]
    
    st.markdown("---")
    # Análise
    custo_mensal = df_filtrado.groupby(df_filtrado['Mes/Ano'].astype(str))['ValorTotal'].sum().reset_index()
    fig = px.bar(custo_mensal, x='Mes/Ano', y='ValorTotal', title=f"Custo Mensal para {empresa} em {regiao}", text_auto='.2s')
    st.plotly_chart(fig, use_container_width=True)

def pagina_estoque():
    st.title("📦 Análise de Estoque")
    st.info("Página em construção.")
    # Aqui entraria a lógica da página de estoque

# --- NAVEGAÇÃO PRINCIPAL ---
# Usando o componente option_menu para criar o menu superior
selecao = option_menu(
    menu_title=None,  # Não queremos um título para o menu
    options=["Manutenção", "Estoque"],  # Nomes das "páginas"
    icons=["wrench", "box-seam"],  # Ícones do Bootstrap Icons
    menu_icon="cast",  # Ícone do menu (opcional)
    default_index=0,  # Começa na primeira opção
    orientation="horizontal", # ESSENCIAL para o menu ficar no topo
)

# --- RENDERIZAÇÃO DA PÁGINA SELECIONADA ---
if selecao == "Manutenção":
    pagina_manutencao()
elif selecao == "Estoque":
    pagina_estoque()

