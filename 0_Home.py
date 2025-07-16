
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Clínica", page_icon="🏥", layout="wide")

df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])

st.title("📊 Painel Geral da Clínica")

# Filtro por período único
data_ini = st.date_input("📅 Data Inicial", df["Data"].min())
data_fim = st.date_input("📅 Data Final", df["Data"].max())
df_filtrado = df[(df["Data"] >= pd.to_datetime(data_ini)) & (df["Data"] <= pd.to_datetime(data_fim))]

df_real = df_filtrado[df_filtrado["Status"] == "Realizada"]
df_cancel = df_filtrado[df_filtrado["Status"] == "Cancelada"]

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("✅ Atendimentos", len(df_real))
col2.metric("💰 Faturamento", f"R$ {df_real['Valor'].sum():,.2f}")
ocupadas = df_filtrado[df_filtrado["Ocupada"] == "Sim"]
taxa = (len(ocupadas) / len(df_filtrado)) * 100 if len(df_filtrado) else 0
col3.metric("📈 Ocupação", f"{taxa:.1f}%")
col4.metric("🚫 Cancelamentos", len(df_cancel))
top_prof = df_real['Profissional'].value_counts().idxmax() if not df_real.empty else "-"
col5.metric("🏆 Top Profissional", top_prof)
top_sala = df_real['Sala'].value_counts().idxmax() if not df_real.empty else "-"
col6.metric("📍 Sala Mais Usada", top_sala)

st.markdown("---")

st.subheader("📅 Evolução dos Atendimentos")
atend_dia = df_real.groupby("Data").size().reset_index(name="Total")
fig = px.line(atend_dia, x="Data", y="Total", markers=True, line_shape="linear", color_discrete_sequence=["#B22222"])
st.plotly_chart(fig, use_container_width=True)

st.subheader("👨‍⚕️ Ranking de Produtividade (Atendimentos)")
rank = df_real['Profissional'].value_counts().reset_index()
rank.columns = ["Profissional", "Atendimentos"]
st.dataframe(rank, use_container_width=True)

st.subheader("📋 Últimos Atendimentos")
recentes = df_real.sort_values(by="Data", ascending=False).head(10)
st.dataframe(recentes[["Data", "Profissional", "Sala", "Plano", "Forma_Pagamento", "Valor"]], use_container_width=True)
