import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Monitoramento de Salas", page_icon="🖥️", layout="wide")
st.title("🖥️ Monitoramento de Salas")

# 1) Carrega dados e converte
df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])
df["Hora"] = df["Horário"].str.slice(0,2).astype(int)
df["DiaSemana"] = df["Data"].dt.day_name()

# 2) Filtro de período
col1, col2 = st.columns(2)
dt_ini = col1.date_input("Data Início", df["Data"].min(), key="ms_ini")
dt_fim = col2.date_input("Data Fim",    df["Data"].max(), key="ms_fim")
# converte as datas para Timestamp
dt_ini = pd.to_datetime(dt_ini)
dt_fim = pd.to_datetime(dt_fim)
mask = (df["Data"] >= dt_ini) & (df["Data"] <= dt_fim)
df = df[mask]

# 3) Gera heatmap Hora × Dia
ocup = df[df["Ocupada"] == "Sim"]
pivot = (
    ocup
    .groupby(["Hora","DiaSemana"])
    .size()
    .unstack(fill_value=0)
    .reindex(
        index=sorted(ocup["Hora"].unique()),
        columns=["Monday","Tuesday","Wednesday","Thursday","Friday"],
        fill_value=0
    )
)

st.subheader("📊 Heatmap de Ocupação (Hora × Dia)")

fig = px.imshow(
    pivot,
    labels={"x":"Dia da Semana", "y":"Hora", "color":"Sessões"},
    x=pivot.columns,
    y=pivot.index,
    color_continuous_scale="Reds"
)
fig.update_yaxes(dtick=1)  # mostra cada hora
st.plotly_chart(fig, use_container_width=True)
