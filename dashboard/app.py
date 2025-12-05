import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuração da Página ---
st.set_page_config(page_title="Dashboard Big Data", layout="wide")

# --- Conexão com MinIO ---
# Usamos s3:// porque a lib s3fs entende assim
MINIO_OPTS = {
    "key": "admin",
    "secret": "password",
    "client_kwargs": {"endpoint_url": "http://minio:9000"}
}
BUCKET = "s3://datalake"

# --- Função de Carregamento de Dados ---
@st.cache_data
def load_data():
    try:
        # Lendo os caminhos EXATOS que o Spark criou
        # Pipeline 1: Estatísticas (Média/Desvio Padrão)
        df_stats = pd.read_parquet(f"{BUCKET}/pipeline1/statistics", storage_options=MINIO_OPTS)
        
        # Pipeline 4: Rentabilidade (Usaremos para KPIs globais)
        df_kpis = pd.read_parquet(f"{BUCKET}/pipeline4/profitability", storage_options=MINIO_OPTS)
        
        return df_stats, df_kpis
    except Exception as e:
        st.error(f"Erro no carregamento: {e}")
        return None, None

df_stats, df_kpis = load_data()

if df_stats is not None and df_kpis is not None:
    st.title("Projeto Final Big Data - Análise de Vendas")
    st.markdown("---")
    
    # --- KPIs Globais ---
    # Somamos a coluna 'Sales' e 'Profit' que vieram do Spark
    total_sales = df_kpis['Sales'].sum()
    total_profit = df_kpis['Profit'].sum()
    avg_margin = (total_profit / total_sales) * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Vendas Totais", f"$ {total_sales:,.2f}")
    col2.metric("Lucro Total", f"$ {total_profit:,.2f}")
    col3.metric("Margem Média", f"{avg_margin:.1f}%")
    
    st.divider()
    
    # --- Gráficos ---
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("Vendas Médias por Subcategoria")
        # Atenção: O Spark gerou a coluna como 'Sub-Category' (com hífen)
        fig_bar = px.bar(df_stats, x="Sub-Category", y="MeanSales", 
                         title="Média de Vendas", color="MeanProfit")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_graf2:
        st.subheader("Distribuição do Lucro por Região")
        # Agrupando os dados do Pipeline 4 para o gráfico de pizza
        df_region = df_kpis.groupby("Region")[["Profit"]].sum().reset_index()
        fig_pie = px.pie(df_region, values='Profit', names='Region', 
                         title="Share de Lucratividade", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.warning("Dados ainda não disponíveis.")
    st.info("Certifique-se de ter rodado o Notebook do Spark para gerar os arquivos no MinIO.")