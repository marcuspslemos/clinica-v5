import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Diário de Produção", page_icon="📘", layout="wide")
st.title("📘 Diário de Produção")

# ==== FILTRO DE PERÍODO ====
df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])
ini = st.date_input("Data Início", df.Data.min(), key="dpp_ini")
fim = st.date_input("Data Fim", df.Data.max(), key="dpp_fim")
df = df[(df.Data>=pd.to_datetime(ini)) & (df.Data<=pd.to_datetime(fim))]

# ==== FILTRO DE SALAS ====
salas = st.multiselect("Selecione a(s) Sala(s)", df.Sala.unique(), default=list(df.Sala.unique()))
df = df[df.Sala.isin(salas)]

# ==== MÉTRICAS CENTRADAS ====
ocup = df[df.Ocupada=="Sim"]
cap = len(df)
taxa = ocup.shape[0]/cap*100 if cap else 0

c1, c2, c3 = st.columns(3)
c1.metric("Capacidade Total", f"{cap}")
c2.metric("Ocupadas", f"{ocup.shape[0]}")
c3.metric("Ociosidade", f"{100-taxa:.1f}%")

st.markdown("---")

# ==== BARRAS HORIZONTAIS ====
st.subheader("📊 Ocupação por Sala (horiz.)")
ocup_s = ocup.Sala.value_counts().reset_index()
ocup_s.columns = ["Sala","Sessões"]
fig = px.bar(ocup_s, x="Sessões", y="Sala", orientation="h",
             color="Sala", color_discrete_sequence=px.colors.sequential.Reds)
st.plotly_chart(fig, use_container_width=True)
