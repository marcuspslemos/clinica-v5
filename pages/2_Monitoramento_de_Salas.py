import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Monitoramento de Salas", page_icon="🖥️", layout="wide")
st.title("🖥️ Monitoramento de Salas")

df = pd.read_csv("data/dados_ficticios.csv")
df["DataHora"] = pd.to_datetime(df.Data + " " + df.Horário)
df["Fim"] = df["DataHora"] + pd.Timedelta(minutes=50)

# ==== FILTRO DE PERÍODO ====
ini = st.date_input("Data Início", df.DataHora.min().date(), key="ms_ini")
fim = st.date_input("Data Fim", df.DataHora.max().date(), key="ms_fim")
mask = (df.DataHora.dt.date>=ini) & (df.DataHora.dt.date<=fim)
df = df[mask]

# ==== GRÁFICO DE TIMELINE ====
st.subheader("⏰ Timeline de Ocupação (50 min consulta)")
fig = px.timeline(df[df.Ocupada=="Sim"], x_start="DataHora", x_end="Fim",
                  y="Sala", color="Sala", title="", 
                  color_discrete_sequence=px.colors.sequential.Reds)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)
