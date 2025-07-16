
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Diário de Produção", page_icon="📘", layout="wide")

st.title("📘 Diário de Produção")

df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])

salas = df["Sala"].unique()
sala_selecionada = st.multiselect("Selecione a(s) Sala(s)", salas, default=salas)

df_filtrado = df[df["Sala"].isin(sala_selecionada)]

capacidade_total = len(df_filtrado)
ocupadas = len(df_filtrado[df_filtrado["Ocupada"] == "Sim"])
taxa_ocup = (ocupadas / capacidade_total) * 100 if capacidade_total else 0

st.metric("📌 Capacidade Total", capacidade_total)
st.metric("✅ Ocupadas", ocupadas)
st.metric("📉 Ociosidade", f"{100 - taxa_ocup:.1f}%")

# Gráfico de barras por sala
st.subheader("📊 Ocupação por Sala")
ocupacao_sala = df_filtrado[df_filtrado["Ocupada"] == "Sim"]["Sala"].value_counts().reset_index()
ocupacao_sala.columns = ["Sala", "Sessões"]
fig = px.bar(ocupacao_sala, x="Sala", y="Sessões", color="Sala", text_auto=True, color_discrete_sequence=px.colors.sequential.Reds)
st.plotly_chart(fig, use_container_width=True)
