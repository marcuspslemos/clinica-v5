import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Faturamento", page_icon="💵", layout="wide")
st.title("💵 Faturamento da Clínica")

# 1) Carrega dados e converte data
df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])

# 2) Filtro de período
col1, col2 = st.columns(2)
start = col1.date_input("Data Início", df["Data"].min())
end   = col2.date_input("Data Fim",    df["Data"].max())
mask = (df["Data"] >= pd.to_datetime(start)) & (df["Data"] <= pd.to_datetime(end))
df = df[mask]

# 3) Somente realizados
real = df[df["Status"] == "Realizada"]

# 4) Gráfico por convênio
st.subheader("📋 Faturamento por Convênio")
por_plano = (
    real
    .groupby("Plano")["Valor"]
    .sum()
    .reset_index()
    .sort_values("Valor", ascending=False)
)
fig1 = px.bar(
    por_plano, x="Plano", y="Valor", text_auto=".2f",
    color_discrete_sequence=px.colors.sequential.Reds
)
st.plotly_chart(fig1, use_container_width=True)

# 5) Gráfico por forma de pagamento
st.subheader("💳 Faturamento por Forma de Pagamento")
por_pag = (
    real
    .groupby("Forma_Pagamento")["Valor"]
    .sum()
    .reset_index()
)
fig2 = px.pie(
    por_pag, names="Forma_Pagamento", values="Valor",
    hole=0.4, color_discrete_sequence=px.colors.sequential.Reds
)
st.plotly_chart(fig2, use_container_width=True)
