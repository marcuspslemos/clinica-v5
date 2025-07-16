import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Monitoramento de Salas", page_icon="🖥️", layout="wide")
st.title("🖥️ Monitoramento de Salas")

# 1) Carrega dados e converte colunas
df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])
df["Hora"] = df["Horário"].str.slice(0,2).astype(int)
df["DiaSemana"] = df["Data"].dt.day_name(locale="pt_BR")

# 2) Filtro de período
col1, col2 = st.columns(2)
data_inicio = col1.date_input("Data Início", df["Data"].min())
data_fim    = col2.date_input("Data Fim",    df["Data"].max())
mask = (df["Data"] >= pd.to_datetime(data_inicio)) & (df["Data"] <= pd.to_datetime(data_fim))
df = df[mask]

# 3) Prepara pivot para heatmap
ocup = df[df["Ocupada"] == "Sim"]
pivot = (
    ocup
    .groupby(["Hora","DiaSemana"])
    .size()
    .unstack(fill_value=0)
    .reindex(index=sorted(ocup["Hora"].unique()), columns=["segunda-feira","terça-feira","quarta-feira","quinta-feira","sexta-feira"], fill_value=0)
)

st.subheader("📊 Heatmap de Ocupação (Hora × Dia)")
fig = px.imshow(
    pivot,
    labels=dict(x="Dia da Semana", y="Hora", color="Sessões"),
    x=pivot.columns,
    y=pivot.index,
    color_continuous_scale="Reds"
)
st.plotly_chart(fig, use_container_width=True)
