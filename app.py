# app.py (VERSÃO FINAL COM ANÁLISE DE PERFORMANCE EM TODAS AS ABAS)

import streamlit as st
import pandas as pd
import plotly.express as px
from dateutil.relativedelta import relativedelta

from src.data_provider import get_data

st.set_page_config(page_title="Dashboard de Custos de Frota", layout="wide", page_icon="🚚")

# --- FUNÇÃO DE CÁLCULO DE KPIs (AGORA GENÉRICA) ---
def calcular_kpis_performance(df_historico, ano_selecionado, mes_selecionado, coluna_custo):
    """
    Calcula os KPIs de performance para uma coluna de custo específica.
    Pode ser 'valor' (manutenção), 'custo_combustivel_total' ou 'custo_frota_total'.
    """
    if mes_selecionado == 'Todos' or ano_selecionado == 'Todos':
        return None

    data_base = pd.to_datetime(f"{mes_selecionado}-01")
    mes_anterior = data_base - relativedelta(months=1)
    tres_meses_atras = data_base - relativedelta(months=3)

    df_mes_atual = df_historico[df_historico['mes_ano'] == data_base.strftime('%Y-%m')]
    df_mes_anterior = df_historico[df_historico['mes_ano'] == mes_anterior.strftime('%Y-%m')]
    df_ultimos_3_meses = df_historico[(df_historico['data'] >= tres_meses_atras) & (df_historico['data'] < data_base)]

    custo_mes_atual = df_mes_atual[coluna_custo].sum()
    custo_mes_anterior = df_mes_anterior[coluna_custo].sum()
    custo_ultimos_3_meses = df_ultimos_3_meses[coluna_custo].sum()
    media_3_meses = custo_ultimos_3_meses / 3 if custo_ultimos_3_meses > 0 else 0
    
    dias_uteis_atual = df_mes_atual['Dias Úteis'].iloc[0] if not df_mes_atual.empty and 'Dias Úteis' in df_mes_atual.columns else 0
    dias_uteis_anterior = df_mes_anterior['Dias Úteis'].iloc[0] if not df_mes_anterior.empty and 'Dias Úteis' in df_mes_anterior.columns else 0
    
    custo_dia_util_atual = custo_mes_atual / dias_uteis_atual if dias_uteis_atual > 0 else 0
    custo_dia_util_anterior = custo_mes_anterior / dias_uteis_anterior if dias_uteis_anterior > 0 else 0
    
    soma_dias_uteis_3m = df_ultimos_3_meses.groupby('mes_ano')['Dias Úteis'].first().sum() if 'Dias Úteis' in df_ultimos_3_meses.columns else 0
    media_dia_util_3m = custo_ultimos_3_meses / soma_dias_uteis_3m if soma_dias_uteis_3m > 0 else 0

    kpis = {
        'custo_mes_atual': custo_mes_atual, 'custo_mes_anterior': custo_mes_anterior,
        'diff_mes_anterior': custo_mes_atual - custo_mes_anterior, 'media_3_meses': media_3_meses,
        'diff_media_3_meses': custo_mes_atual - media_3_meses, 'custo_dia_util_atual': custo_dia_util_atual,
        'custo_dia_util_anterior': custo_dia_util_anterior, 'diff_dia_util_anterior': custo_dia_util_atual - custo_dia_util_anterior,
        'media_dia_util_3m': media_dia_util_3m, 'diff_media_dia_util_3m': custo_dia_util_atual - media_dia_util_3m
    }
    return kpis

# --- FUNÇÃO PARA GERAR GRÁFICOS DE PERFORMANCE (AGORA GENÉRICA) ---
def exibir_graficos_performance(df_historico, mes_selecionado, kpis, coluna_custo, titulo_grafico):
    """Exibe os gráficos de linha e de barras para a análise de performance."""
    st.subheader("Visualização da Performance Temporal")
    g_col1, g_col2 = st.columns(2)

    with g_col1:
        doze_meses_atras = (pd.to_datetime(f"{mes_selecionado}-01") - relativedelta(months=11)).strftime('%Y-%m')
        df_grafico_linha = df_historico[df_historico['mes_ano'] >= doze_meses_atras]
        evolucao_mensal = df_grafico_linha.groupby('mes_ano')[coluna_custo].sum().reset_index()
        
        fig_linha = px.line(evolucao_mensal, x='mes_ano', y=coluna_custo,
                            title=f'Evolução do {titulo_grafico} (Últimos 12 Meses)',
                            markers=True, labels={'mes_ano': 'Mês', coluna_custo: 'Custo Total'})
        st.plotly_chart(fig_linha, use_container_width=True)

    with g_col2:
        dados_comparativo = {
            'Período': ['Mês Atual', 'Mês Anterior', 'Média 3 Meses'],
            'Custo Total': [kpis['custo_mes_atual'], kpis['custo_mes_anterior'], kpis['media_3_meses']]
        }
        df_comparativo = pd.DataFrame(dados_comparativo)
        
        fig_bar_comp = px.bar(df_comparativo, x='Período', y='Custo Total',
                              title=f'Comparativo de {titulo_grafico}', text_auto='.2s',
                              color='Período', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_bar_comp.update_layout(showlegend=False)
        st.plotly_chart(fig_bar_comp, use_container_width=True)

# --- CARREGAMENTO E FILTROS (sem alterações) ---
with st.spinner('Analisando a planilha de controle... ☕'):
    df = get_data()

if not df.empty:
    # --- MUDANÇA AQUI: Pré-calculando colunas de custo total para facilitar o uso ---
    df['custo_combustivel_total'] = df['custo_combustivel'] + df['custo_arla']
    df['custo_frota_total'] = df['valor'] + df['custo_combustivel_total']

    with st.sidebar:
        st.title("Análise de Frota")
        selected = st.radio("Selecione a Análise:", options=["Visão Geral", "Manutenção", "Combustível", "Análise Detalhada"], horizontal=True)

    st.header("Painel de Controle")
    with st.expander("Clique para expandir ou recolher os filtros", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            anos_disponiveis = ['Todos'] + sorted(df['ano'].unique().tolist(), reverse=True)
            ano_selecionado = st.selectbox("Ano", options=anos_disponiveis)
        mes_selecionado = 'Todos'
        with col2:
            if ano_selecionado != 'Todos':
                df_ano_filtrado = df[df['ano'] == ano_selecionado]
                meses_disponiveis = ['Todos'] + sorted(df_ano_filtrado['mes_ano'].unique().tolist())
                mes_selecionado = st.selectbox("Mês", options=meses_disponiveis)
        with col3:
            regioes_disponiveis = ['Todos'] + sorted(df['regiao'].unique().tolist())
            regiao_selecionada = st.selectbox("Região", options=regioes_disponiveis)
        with col4:
            if regiao_selecionada != 'Todos':
                df_regiao_filtrada = df[df['regiao'] == regiao_selecionada]
                filiais_disponiveis = ['Todos'] + sorted(df_regiao_filtrada['filial'].unique().tolist())
                filial_selecionada = st.selectbox("Filial", options=filiais_disponiveis)
            else:
                filiais_disponiveis = ['Todos'] + sorted(df['filial'].unique().tolist())
                filial_selecionada = st.selectbox("Filial", options=filiais_disponiveis)

    df_filtrado = df.copy()
    if ano_selecionado != 'Todos': df_filtrado = df_filtrado[df_filtrado['ano'] == ano_selecionado]
    if mes_selecionado != 'Todos': df_filtrado = df_filtrado[df_filtrado['mes_ano'] == mes_selecionado]
    if regiao_selecionada != 'Todos': df_filtrado = df_filtrado[df_filtrado['regiao'] == regiao_selecionada]
    if filial_selecionada != 'Todos': df_filtrado = df_filtrado[df_filtrado['filial'] == filial_selecionada]

    st.markdown("---")

    if filial_selecionada == 'Todos':
        titulo_principal = "Gritsch Transportes"
    else:
        titulo_principal = filial_selecionada.title()

    # --- ABA VISÃO GERAL (COM ANÁLISE DE PERFORMANCE) ---
    if selected == "Visão Geral":
        st.title(f"📊 Visão Geral dos Custos - {titulo_principal}")
        if df_filtrado.empty:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
        else:
            kpis_geral = calcular_kpis_performance(df, ano_selecionado, mes_selecionado, 'custo_frota_total')
            if kpis_geral:
                st.subheader("Indicadores de Performance (Custo Total da Frota)")
                st.write("##### Análise de Custo Total")
                kpi_cols1 = st.columns(4)
                kpi_cols1[0].metric("Custo Total Mês Atual", f"R$ {kpis_geral['custo_mes_atual']:,.2f}")
                kpi_cols1[1].metric("vs. Mês Anterior", f"R$ {kpis_geral['diff_mes_anterior']:,.2f}", delta_color="inverse")
                kpi_cols1[2].metric("Média dos Últimos 3 Meses", f"R$ {kpis_geral['media_3_meses']:,.2f}")
                kpi_cols1[3].metric("vs. Média 3 Meses", f"R$ {kpis_geral['diff_media_3_meses']:,.2f}", delta_color="inverse")
                st.write("##### Análise de Custo por Dia Útil")
                kpi_cols2 = st.columns(4)
                kpi_cols2[0].metric("Custo/Dia Útil Mês Atual", f"R$ {kpis_geral['custo_dia_util_atual']:,.2f}")
                kpi_cols2[1].metric("vs. Mês Anterior", f"R$ {kpis_geral['diff_dia_util_anterior']:,.2f}", delta_color="inverse")
                kpi_cols2[2].metric("Média/Dia Útil dos Últimos 3 Meses", f"R$ {kpis_geral['media_dia_util_3m']:,.2f}")
                kpi_cols2[3].metric("vs. Média 3 Meses", f"R$ {kpis_geral['diff_media_dia_util_3m']:,.2f}", delta_color="inverse")
                exibir_graficos_performance(df, mes_selecionado, kpis_geral, 'custo_frota_total', 'Custo Total da Frota')
                st.markdown("---")
            else:
                st.info("Selecione um ano e um mês específicos para ver a análise de performance.")
            
            # Restante da Visão Geral
            custo_manutencao_total = df_filtrado['valor'].sum()
            custo_combustivel_total = df_filtrado['custo_combustivel_total'].sum()
            st.subheader("Detalhamento dos Custos por Macro Categoria")
            # ... (código dos gráficos e tabela da Visão Geral sem alterações)
            dados_grafico_geral = {'Categoria': ['Manutenção', 'Combustível e Arla'], 'Custo': [custo_manutencao_total, custo_combustivel_total]}
            df_grafico_geral = pd.DataFrame(dados_grafico_geral).sort_values('Custo', ascending=False)
            cores_geral = ['#007bff', '#28a745']
            mapa_cores_geral = {'Manutenção': cores_geral[0], 'Combustível e Arla': cores_geral[1]}
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                fig_pie_geral = px.pie(df_grafico_geral, names='Categoria', values='Custo', title='Distribuição Percentual dos Custos', hole=.3, color='Categoria', color_discrete_map=mapa_cores_geral)
                fig_pie_geral.update_traces(textposition='outside', textinfo='percent+label')
                fig_pie_geral.update_layout(legend_font_size=14, uniformtext_minsize=12, uniformtext_mode='hide')
                st.plotly_chart(fig_pie_geral, use_container_width=True)
            with g_col2:
                fig_bar_geral = px.bar(df_grafico_geral, x='Categoria', y='Custo', text_auto='.2s', title='Comparativo de Custos por Macro Categoria', color='Categoria', color_discrete_map=mapa_cores_geral)
                fig_bar_geral.update_layout(showlegend=False)
                fig_bar_geral.update_traces(width=0.4, textangle=0, textposition="outside")
                fig_bar_geral.update_yaxes(range=[0, df_grafico_geral['Custo'].max() * 1.1])
                st.plotly_chart(fig_bar_geral, use_container_width=True)
            st.markdown("---")
            st.subheader(f"Relatório Detalhado por Veículo - {titulo_principal}")
            df_detalhado = df_filtrado.groupby('Placa').agg({'Modelo': 'first', 'Grupo Veículo': 'first', 'Marca': 'first', 'TP.Comb': 'first', 'TP.Rota': 'first', 'contrato': 'first', 'Roteiro Principal': 'first', 'Motorista Principal': 'first', 'custo_combustivel': 'sum', 'custo_arla': 'sum', 'custo_manutencao_geral': 'sum', 'custo_rodas_pneus': 'sum', 'custo_lataria_pintura': 'sum'}).reset_index()
            df_detalhado['Custo Total'] = df_detalhado[['custo_combustivel', 'custo_arla', 'custo_manutencao_geral', 'custo_rodas_pneus', 'custo_lataria_pintura']].sum(axis=1)
            df_detalhado.rename(columns={'custo_combustivel': 'Valor Comb.', 'custo_arla': 'Arla', 'custo_manutencao_geral': 'Manutenção em Geral', 'custo_rodas_pneus': 'Rodas / Pneus', 'custo_lataria_pintura': 'Lataria e Pintura', 'contrato': 'Contrato', 'TP.Comb': 'Tipo Combustível', 'TP.Rota': 'Tipo de Rota'}, inplace=True)
            ordem_colunas_detalhado = ['Placa', 'Modelo', 'Marca', 'Grupo Veículo', 'Tipo Combustível', 'Tipo de Rota', 'Contrato', 'Roteiro Principal', 'Motorista Principal', 'Valor Comb.', 'Arla', 'Manutenção em Geral', 'Rodas / Pneus', 'Lataria e Pintura', 'Custo Total']
            st.dataframe(df_detalhado[ordem_colunas_detalhado], use_container_width=True, hide_index=True, column_config={"Custo Total": st.column_config.NumberColumn(format="R$ %.2f"), "Valor Comb.": st.column_config.NumberColumn(format="R$ %.2f"), "Arla": st.column_config.NumberColumn(format="R$ %.2f"), "Manutenção em Geral": st.column_config.NumberColumn(format="R$ %.2f"), "Rodas / Pneus": st.column_config.NumberColumn(format="R$ %.2f"), "Lataria e Pintura": st.column_config.NumberColumn(format="R$ %.2f")})

    # --- ABA MANUTENÇÃO (COM ANÁLISE DE PERFORMANCE) ---
    if selected == "Manutenção":
        st.title(f"🛠️ Análise de Manutenção - {titulo_principal}")
        if df_filtrado.empty:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
        else:
            kpis_manutencao = calcular_kpis_performance(df, ano_selecionado, mes_selecionado, 'valor')
            if kpis_manutencao:
                st.subheader("Indicadores de Performance (Custo de Manutenção)")
                st.write("##### Análise de Custo Total")
                kpi_cols1 = st.columns(4)
                kpi_cols1[0].metric("Custo Total Mês Atual", f"R$ {kpis_manutencao['custo_mes_atual']:,.2f}")
                kpi_cols1[1].metric("vs. Mês Anterior", f"R$ {kpis_manutencao['diff_mes_anterior']:,.2f}", delta_color="inverse")
                kpi_cols1[2].metric("Média dos Últimos 3 Meses", f"R$ {kpis_manutencao['media_3_meses']:,.2f}")
                kpi_cols1[3].metric("vs. Média 3 Meses", f"R$ {kpis_manutencao['diff_media_3_meses']:,.2f}", delta_color="inverse")
                st.write("##### Análise de Custo por Dia Útil")
                kpi_cols2 = st.columns(4)
                kpi_cols2[0].metric("Custo/Dia Útil Mês Atual", f"R$ {kpis_manutencao['custo_dia_util_atual']:,.2f}")
                kpi_cols2[1].metric("vs. Mês Anterior", f"R$ {kpis_manutencao['diff_dia_util_anterior']:,.2f}", delta_color="inverse")
                kpi_cols2[2].metric("Média/Dia Útil dos Últimos 3 Meses", f"R$ {kpis_manutencao['media_dia_util_3m']:,.2f}")
                kpi_cols2[3].metric("vs. Média 3 Meses", f"R$ {kpis_manutencao['diff_media_dia_util_3m']:,.2f}", delta_color="inverse")
                exibir_graficos_performance(df, mes_selecionado, kpis_manutencao, 'valor', 'Custo de Manutenção')
                st.markdown("---")
            else:
                st.info("Selecione um ano e um mês específicos para ver a análise de performance.")

            # Restante da aba Manutenção
            st.subheader("Detalhamento dos Custos por Categoria")
            # ... (código dos gráficos e tabela da Manutenção sem alterações)
            custo_lataria = df_filtrado['custo_lataria_pintura'].sum()
            custo_manutencao = df_filtrado['custo_manutencao_geral'].sum()
            custo_rodas = df_filtrado['custo_rodas_pneus'].sum()
            kpi_cols = st.columns(3)
            kpi_cols[0].metric("Manutenção Geral", f"R$ {custo_manutencao:,.2f}")
            kpi_cols[1].metric("Rodas e Pneus", f"R$ {custo_rodas:,.2f}")
            kpi_cols[2].metric("Lataria e Pintura", f"R$ {custo_lataria:,.2f}")
            st.markdown("---")
            st.subheader(f"Análise Visual dos Custos - {titulo_principal}")
            dados_grafico = {'Categoria': ['Manutenção Geral', 'Rodas e Pneus', 'Lataria e Pintura'], 'Custo': [custo_manutencao, custo_rodas, custo_lataria]}
            df_grafico = pd.DataFrame(dados_grafico).sort_values('Custo', ascending=False)
            cores_vivas = ["#1b69a0", '#ff7f0e', '#2ca02c']
            mapa_cores = {'Manutenção Geral': cores_vivas[0], 'Rodas e Pneus': cores_vivas[1], 'Lataria e Pintura': cores_vivas[2]}
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                fig_pie = px.pie(df_grafico, names='Categoria', values='Custo', title='Distribuição Percentual dos Custos', hole=.3, color='Categoria', color_discrete_map=mapa_cores)
                fig_pie.update_traces(textposition='outside', textinfo='percent+label')
                fig_pie.update_layout(legend_font_size=14, uniformtext_minsize=12, uniformtext_mode='hide')
                st.plotly_chart(fig_pie, use_container_width=True)
            with g_col2:
                fig_bar = px.bar(df_grafico, x='Categoria', y='Custo', text_auto='.2s', title='Comparativo de Custos por Categoria', color='Categoria', color_discrete_map=mapa_cores)
                fig_bar.update_layout(showlegend=False)
                fig_bar.update_traces(width=0.5, textangle=0, textposition="outside")
                fig_bar.update_yaxes(range=[0, df_grafico['Custo'].max() * 1.1])
                st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("---")
            st.subheader(f"Detalhamento por Veículo - {titulo_principal}")
            df_veiculos = df_filtrado.groupby('Placa').agg({'Modelo': 'first', 'Grupo Veículo': 'first', 'Marca': 'first', 'TP.Comb': 'first', 'TP.Rota': 'first', 'contrato': 'first', 'Roteiro Principal': 'first', 'Motorista Principal': 'first', 'custo_manutencao_geral': 'sum', 'custo_rodas_pneus': 'sum', 'custo_lataria_pintura': 'sum', 'valor': 'sum'}).reset_index()
            df_veiculos.rename(columns={'valor': 'Custo Total', 'custo_manutencao_geral': 'Manutenção Geral', 'custo_rodas_pneus': 'Rodas e Pneus', 'custo_lataria_pintura': 'Lataria e Pintura', 'contrato': 'Contrato'}, inplace=True)
            ordem_colunas = ['Placa', 'Modelo', 'Marca', 'Grupo Veículo', 'TP.Comb', 'TP.Rota', 'Contrato', 'Roteiro Principal', 'Motorista Principal', 'Manutenção Geral', 'Rodas e Pneus', 'Lataria e Pintura', 'Custo Total']
            st.dataframe(df_veiculos[ordem_colunas], use_container_width=True, hide_index=True, column_config={"Custo Total": st.column_config.NumberColumn(format="R$ %.2f"), "Manutenção Geral": st.column_config.NumberColumn(format="R$ %.2f"), "Rodas e Pneus": st.column_config.NumberColumn(format="R$ %.2f"), "Lataria e Pintura": st.column_config.NumberColumn(format="R$ %.2f")})

    # --- ABA COMBUSTÍVEL (COM ANÁLISE DE PERFORMANCE) ---
    if selected == "Combustível":
        st.title(f"⛽ Análise de Combustível e Arla - {titulo_principal}")
        if df_filtrado.empty:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
        else:
            kpis_combustivel = calcular_kpis_performance(df, ano_selecionado, mes_selecionado, 'custo_combustivel_total')
            if kpis_combustivel:
                st.subheader("Indicadores de Performance (Custo de Combustível)")
                st.write("##### Análise de Custo Total")
                kpi_cols1 = st.columns(4)
                kpi_cols1[0].metric("Custo Total Mês Atual", f"R$ {kpis_combustivel['custo_mes_atual']:,.2f}")
                kpi_cols1[1].metric("vs. Mês Anterior", f"R$ {kpis_combustivel['diff_mes_anterior']:,.2f}", delta_color="inverse")
                kpi_cols1[2].metric("Média dos Últimos 3 Meses", f"R$ {kpis_combustivel['media_3_meses']:,.2f}")
                kpi_cols1[3].metric("vs. Média 3 Meses", f"R$ {kpis_combustivel['diff_media_3_meses']:,.2f}", delta_color="inverse")
                st.write("##### Análise de Custo por Dia Útil")
                kpi_cols2 = st.columns(4)
                kpi_cols2[0].metric("Custo/Dia Útil Mês Atual", f"R$ {kpis_combustivel['custo_dia_util_atual']:,.2f}")
                kpi_cols2[1].metric("vs. Mês Anterior", f"R$ {kpis_combustivel['diff_dia_util_anterior']:,.2f}", delta_color="inverse")
                kpi_cols2[2].metric("Média/Dia Útil dos Últimos 3 Meses", f"R$ {kpis_combustivel['media_dia_util_3m']:,.2f}")
                kpi_cols2[3].metric("vs. Média 3 Meses", f"R$ {kpis_combustivel['diff_media_dia_util_3m']:,.2f}", delta_color="inverse")
                exibir_graficos_performance(df, mes_selecionado, kpis_combustivel, 'custo_combustivel_total', 'Custo de Combustível')
                st.markdown("---")
            else:
                st.info("Selecione um ano e um mês específicos para ver a análise de performance.")

            # Restante da aba Combustível
            st.subheader(f"Análise Visual dos Custos - {titulo_principal}")
            # ... (código dos gráficos e tabela de Combustível sem alterações)
            custo_combustivel = df_filtrado['custo_combustivel'].sum()
            custo_arla = df_filtrado['custo_arla'].sum()
            dados_grafico_comb = {'Categoria': ['Combustível', 'Arla'], 'Custo': [custo_combustivel, custo_arla]}
            df_grafico_comb = pd.DataFrame(dados_grafico_comb).sort_values('Custo', ascending=False)
            cores_comb = ["#e02222", "#1410e0"] 
            mapa_cores_comb = {'Combustível': cores_comb[0], 'Arla': cores_comb[1]}
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                fig_pie_comb = px.pie(df_grafico_comb, names='Categoria', values='Custo', title='Distribuição Percentual dos Custos', hole=.3, color='Categoria', color_discrete_map=mapa_cores_comb)
                fig_pie_comb.update_traces(textposition='outside', textinfo='percent+label')
                fig_pie_comb.update_layout(legend_font_size=14, uniformtext_minsize=12, uniformtext_mode='hide')
                st.plotly_chart(fig_pie_comb, use_container_width=True)
            with g_col2:
                fig_bar_comb = px.bar(df_grafico_comb, x='Categoria', y='Custo', text_auto='.2s', title='Comparativo de Custos por Categoria', color='Categoria', color_discrete_map=mapa_cores_comb)
                fig_bar_comb.update_layout(showlegend=False)
                fig_bar_comb.update_traces(width=0.4, textangle=0, textposition="outside")
                fig_bar_comb.update_yaxes(range=[0, df_grafico_comb['Custo'].max() * 1.1])
                st.plotly_chart(fig_bar_comb, use_container_width=True)
            st.markdown("---")
            st.subheader(f"Detalhamento por Veículo - {titulo_principal}")
            df_veiculos_comb = df_filtrado.groupby('Placa').agg({'Modelo': 'first', 'Grupo Veículo': 'first', 'Marca': 'first', 'TP.Comb': 'first', 'TP.Rota': 'first', 'contrato': 'first', 'Roteiro Principal': 'first', 'Motorista Principal': 'first', 'custo_combustivel': 'sum', 'custo_arla': 'sum'}).reset_index()
            df_veiculos_comb['Custo Total'] = df_veiculos_comb['custo_combustivel'] + df_veiculos_comb['custo_arla']
            df_veiculos_comb.rename(columns={'custo_combustivel': 'Custo Combustível', 'custo_arla': 'Custo Arla', 'contrato': 'Contrato'}, inplace=True)
            ordem_colunas_comb = ['Placa', 'Modelo', 'Marca', 'Grupo Veículo', 'TP.Comb', 'TP.Rota', 'Contrato', 'Roteiro Principal', 'Motorista Principal', 'Custo Combustível', 'Custo Arla', 'Custo Total']
            st.dataframe(df_veiculos_comb[ordem_colunas_comb], use_container_width=True, hide_index=True, column_config={"Custo Total": st.column_config.NumberColumn(format="R$ %.2f"), "Custo Combustível": st.column_config.NumberColumn(format="R$ %.2f"), "Custo Arla": st.column_config.NumberColumn(format="R$ %.2f")})

    # --- ABA ANÁLISE DETALHADA (sem alterações) ---
    if selected == "Análise Detalhada":
        st.title("🔍 Análise Detalhada dos Dados")
        st.info("Os dados abaixo refletem os filtros aplicados no Painel de Controle.")
        if not df_filtrado.empty:
            st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic")
