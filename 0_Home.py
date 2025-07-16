import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Clínica", page_icon="🏥", layout="wide")

df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])

st.title("📊 Painel Geral da Clínica")

# === Centralizando cards em 3 colunas ===
col1, col2, col3 = st.columns(3)
# Indicadores exemplo (você pode ajustar os 6 aqui)
col1.metric("Atendimentos", len(df[df.Status=="Realizada"]))
col2.metric("Faturamento", f"R$ {df[df.Status=="Realizada"].Valor.sum():,.2f}")
col3.metric("Cancelamentos", len(df[df.Status=="Cancelada"]))

col4, col5, col6 = st.columns(3)
col4.metric("Ocupação", f"{len(df[df.Ocupada=='Sim'])/len(df)*100:.1f}%")
col5.metric("Top Profissional", df[df.Status=="Realizada"].Profissional.value_counts().idxmax())
col6.metric("Sala Mais Usada", df[df.Status=="Realizada"].Sala.value_counts().idxmax())

st.markdown("---")

# Evolução de atendimentos
st.subheader("📅 Evolução dos Atendimentos")
data_ini = st.date_input("De", df.Data.min(), key="home_ini")
data_fim = st.date_input("Até", df.Data.max(), key="home_fim")
df_f = df[(df.Data>=pd.to_datetime(data_ini)) & (df.Data<=pd.to_datetime(data_fim)) & (df.Status=="Realizada")]

evol = df_f.groupby("Data").size().reset_index(name="Total")
fig = px.line(evol, x="Data", y="Total", markers=True,
              title="", color_discrete_sequence=["#b71c1c"])
st.plotly_chart(fig, use_container_width=True)
