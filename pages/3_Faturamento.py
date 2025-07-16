import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Faturamento", page_icon="💵", layout="wide")
st.title("💵 Faturamento da Clínica")

df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])
df = df[(df.Data>=st.date_input("Data Início", df.Data.min(), key="fat_ini")) &
        (df.Data<=st.date_input("Data Fim", df.Data.max(), key="fat_fim"))]

real = df[df.Status=="Realizada"]

st.subheader("📋 Faturamento por Convênio")
pl = real.groupby("Plano").Valor.sum().reset_index().sort_values("Valor",ascending=False)
st.plotly_chart(px.bar(pl, x="Plano", y="Valor", text_auto=True,
                       color_discrete_sequence=px.colors.sequential.Reds),
                use_container_width=True)

st.subheader("💳 Faturamento por Pagamento")
pg = real.groupby("Forma_Pagamento").Valor.sum().reset_index()
st.plotly_chart(px.pie(pg, names="Forma_Pagamento", values="Valor",
                       hole=0.4, color_discrete_sequence=px.colors.sequential.Reds),
                use_container_width=True)
