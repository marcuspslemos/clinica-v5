
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Monitoramento de Salas", page_icon="🖥️", layout="wide")

st.title("🖥️ Monitoramento de Salas")

df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])

# Gráfico de ocupação por turno
st.subheader("⏰ Ocupação por Turno")
turno_data = df[df["Ocupada"] == "Sim"].groupby("Turno").size().reset_index(name="Total")
fig_turno = px.pie(turno_data, names="Turno", values="Total", hole=0.5, color_discrete_sequence=px.colors.sequential.Reds)
st.plotly_chart(fig_turno, use_container_width=True)
