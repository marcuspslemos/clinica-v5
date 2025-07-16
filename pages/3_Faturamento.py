
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Faturamento", page_icon="💵", layout="wide")

st.title("💵 Faturamento da Clínica")

df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])
df_real = df[df["Status"] == "Realizada"]

# Faturamento por Plano
st.subheader("📋 Faturamento por Convênio")
por_plano = df_real.groupby("Plano")["Valor"].sum().reset_index().sort_values(by="Valor", ascending=False)
fig1 = px.bar(por_plano, x="Plano", y="Valor", text_auto=True, color="Plano", color_discrete_sequence=px.colors.sequential.Reds)
st.plotly_chart(fig1, use_container_width=True)

# Faturamento por Forma de Pagamento
st.subheader("💳 Faturamento por Forma de Pagamento")
por_pagamento = df_real.groupby("Forma_Pagamento")["Valor"].sum().reset_index()
fig2 = px.pie(por_pagamento, names="Forma_Pagamento", values="Valor", hole=0.4, color_discrete_sequence=px.colors.sequential.Reds)
st.plotly_chart(fig2, use_container_width=True)
