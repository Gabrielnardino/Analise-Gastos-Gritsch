# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta
from streamlit_option_menu import option_menu

from src.data_processing import get_processed_data

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard de Manutenção", layout="wide", page_icon="🛠️")

# --- CONSTANTES E FUNÇÕES ---
NATUREZAS_MANUTENCAO = {
    'Manutenção Total': ['03.03 - MANUTENÇÃO DE VEÍCULOS', '03.05 - RODAS E PNEUS', '03.02 - LATARIA E PINTURA', '03.04 - ACESSÓRIOS DE VEÍCULOS'],
    'Manutenção de Veículos': ['03.03 - MANUTENÇÃO DE VEÍCULOS'], 'Rodas e Pneus': ['03.05 - RODAS E PNEUS'],
    'Lataria e Pintura': ['03.02 - LATARIA E PINTURA'], 'Acessórios': ['03.04 - ACESSÓRIOS DE VEÍCULOS']
}

# --- FUNÇÃO DE KPI CORRIGIDA ---
def calcular_kpis(df_filtrado, mes_selecionado_str):
    """Calcula os KPIs com base no mês selecionado."""
    if mes_selecionado_str == "Mês Atual":
        data_base = datetime.now()
    else:
        data_base = datetime.strptime(mes_selecionado_str + '-01', '%Y-%m-%d')

    mes_analise_inicio = data_base.replace(day=1)
    mes_anterior_inicio = mes_analise_inicio - relativedelta(months=1)
    seis_meses_atras = mes_analise_inicio - relativedelta(months=6)
    
    # --- CORREÇÃO APLICADA AQUI ---
    # Filtra o dataframe comparando o ano e o mês diretamente, em vez de usar to_period() em um datetime.
    df_mes_analise = df_filtrado[
        (df_filtrado['data'].dt.year == mes_analise_inicio.year) &
        (df_filtrado['data'].dt.month == mes_analise_inicio.month)
    ]
    
    df_mes_anterior = df_filtrado[
        (df_filtrado['data'].dt.year == mes_anterior_inicio.year) &
        (df_filtrado['data'].dt.month == mes_anterior_inicio.month)
    ]
    # --- FIM DA CORREÇÃO ---

    df_ultimos_6_meses = df_filtrado[(df_filtrado['data'] >= seis_meses_atras) & (df_filtrado['data'] < mes_analise_inicio)]
    
    total_mes_analise = df_mes_analise['valor'].sum()
    total_mes_anterior = df_mes_anterior['valor'].sum()
    
    diff_mes_anterior = total_mes_analise - total_mes_anterior
    perc_diff_mes_anterior = (diff_mes_anterior / total_mes_anterior * 100) if total_mes_anterior != 0 else 0
    
    total_ultimos_6_meses = df_ultimos_6_meses['valor'].sum()
    media_6_meses = total_ultimos_6_meses / 6 if total_ultimos_6_meses > 0 else 0
    
    diff_media_6_meses = total_mes_analise - media_6_meses
    perc_diff_media_6_meses = (diff_media_6_meses / media_6_meses * 100) if media_6_meses != 0 else 0

    return {
        "total_mes_analise": total_mes_analise, "total_mes_anterior": total_mes_anterior,
        "diff_mes_anterior": diff_mes_anterior, "perc_diff_mes_anterior": perc_diff_mes_anterior,
        "media_6_meses": media_6_meses, "diff_media_6_meses": diff_media_6_meses,
        "perc_diff_media_6_meses": perc_diff_media_6_meses
    }

# --- CARREGAMENTO DE DADOS ---
with st.spinner('Conectando ao banco e processando os dados... Por favor, aguarde! ☕'):
    df_original, df_rateio = get_processed_data()

# --- LAYOUT PRINCIPAL (sem alterações) ---
if not df_original.empty:
    with st.sidebar:
        st.title("Análise de Frota")
        selected = option_menu(
            menu_title=None,
            options=["Visão Geral", "Análise Detalhada", "Análise de Rateios"],
            icons=["bar-chart-line", "search", "diagram-3"],
            default_index=0,
        )

    st.header("Painel de Controle")
    with st.expander("Clique para expandir ou recolher os filtros", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            meses_disponiveis = sorted(df_original['mes_ano'].unique().tolist(), reverse=True)
            mes_selecionado = st.selectbox("Mês de Análise", options=["Mês Atual"] + meses_disponiveis)
        
        with col2:
            empresa_selecionada = st.selectbox("Empresa", options=['Todas'] + sorted(df_original['empresa'].unique().tolist()))
        
        with col3:
            regiao_selecionada = st.selectbox("Região", options=['Todas'] + sorted(df_original['regiao'].unique().tolist()))

        with col4:
            df_filtrado_temp = df_original.copy()
            if regiao_selecionada != 'Todas':
                df_filtrado_temp = df_filtrado_temp[df_filtrado_temp['regiao'] == regiao_selecionada]
            filial_selecionada = st.selectbox("Filial", options=['Todas'] + sorted(df_filtrado_temp['filial'].unique().tolist()))

    df_filtrado_geral = df_original.copy()
    if empresa_selecionada != 'Todas':
        df_filtrado_geral = df_filtrado_geral[df_filtrado_geral['empresa'] == empresa_selecionada]
    if regiao_selecionada != 'Todas':
        df_filtrado_geral = df_filtrado_geral[df_filtrado_geral['regiao'] == regiao_selecionada]
    if filial_selecionada != 'Todas':
        df_filtrado_geral = df_filtrado_geral[df_filtrado_geral['filial'] == filial_selecionada]

    st.markdown("---")

    if selected == "Visão Geral":
        st.title(f"🛠️ Visão Geral")
        
        natureza_selecionada_key = st.selectbox(
            "Selecione o Tipo de Manutenção para Análise",
            options=list(NATUREZAS_MANUTENCAO.keys())
        )
        df_final_filtrado = df_filtrado_geral[df_filtrado_geral['natureza_correta'].isin(NATUREZAS_MANUTENCAO[natureza_selecionada_key])]

        if df_final_filtrado.empty:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
        else:
            kpis = calcular_kpis(df_final_filtrado, mes_selecionado)
            
            tab1, tab2 = st.tabs(["📈 Indicadores Chave (KPIs)", "📊 Gráficos Detalhados"])

            with tab1:
                st.subheader(f"Performance para o período de '{mes_selecionado}'")
                kpi_cols = st.columns(4)
                kpi_cols[0].metric(label=f"Total em {mes_selecionado}", value=f"R$ {kpis['total_mes_analise']:,.2f}")
                kpi_cols[1].metric(label="Variação vs Mês Anterior", value=f"{kpis['perc_diff_mes_anterior']:.1f}%", delta=f"R$ {kpis['diff_mes_anterior']:,.2f}", delta_color="inverse")
                kpi_cols[2].metric(label="Média dos Últimos 6 Meses", value=f"R$ {kpis['media_6_meses']:,.2f}")
                kpi_cols[3].metric(label="Variação vs Média 6M", value=f"{kpis['perc_diff_media_6_meses']:.1f}%", delta=f"R$ {kpis['diff_media_6_meses']:,.2f}", delta_color="inverse")

            with tab2:
                st.subheader("Evolução Mensal dos Custos (últimos 12 meses)")
                doze_meses_atras = (datetime.now() - relativedelta(months=12)).strftime('%Y-%m')
                df_grafico = df_final_filtrado[df_final_filtrado['mes_ano'] >= doze_meses_atras]
                custo_mensal = df_grafico.groupby('mes_ano')['valor'].sum().reset_index()
                
                fig = px.bar(custo_mensal, x='mes_ano', y='valor', text_auto='.2s', title="Custo Total por Mês",
                             labels={'mes_ano': 'Mês/Ano', 'valor': 'Custo Total (R$)'})
                fig.update_traces(textangle=0, textposition="outside")
                st.plotly_chart(fig, use_container_width=True)

    if selected == "Análise Detalhada":
        st.title("🔍 Análise Detalhada dos Dados")
        st.info("Os dados abaixo refletem os filtros de Mês, Empresa, Região e Filial. O tipo de manutenção não é aplicado nesta tela.")
        if not df_filtrado_geral.empty:
            st.data_editor(df_filtrado_geral, use_container_width=True, num_rows="dynamic")
        else:
            st.warning("Nenhum dado para exibir com os filtros atuais.")

    if selected == "Análise de Rateios":
        st.title("📦 Análise de Registros de Rateio")
        st.info("Esta seção mostra todos os registros que foram classificados como 'RATEIO' por não terem uma região mapeada. Eles foram excluídos das análises principais.")
        if not df_rateio.empty:
            st.dataframe(df_rateio)
        else:
            st.success("Nenhum registro de rateio foi encontrado nos dados atuais.")

else:
    st.error("Não foi possível carregar os dados para exibir o dashboard.")
