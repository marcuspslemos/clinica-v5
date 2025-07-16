import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comparativo de Períodos", page_icon="🆚", layout="wide")
st.title("🆚 Comparativo entre Períodos")

df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])

# Dois seletores de intervalo
p1 = st.date_input("Período 1", [df.Data.min(), df.Data.min()+pd.Timedelta(days=7)], key="cp1")
p2 = st.date_input("Período 2", [df.Data.min()+pd.Timedelta(days=8), df.Data.max()], key="cp2")

# Métricas de função auxiliar
def m(d):
    r = d[d.Status=="Realizada"]; c = d[d.Status=="Cancelada"]
    return len(r), r.Valor.sum(), len(c), (r.Profissional.value_counts().idxmax() if not r.empty else "-")

df1 = df[(df.Data>=p1[0])&(df.Data<=p1[1])]
df2 = df[(df.Data>=p2[0])&(df.Data<=p2[1])]

m1 = m(df1); m2 = m(df2)
labels = ["Atendimentos","Faturamento","Cancelamentos","Top Profissional"]

cols = st.columns(4)
for i, lab in enumerate(labels):
    v1, v2 = m1[i], m2[i]
    delta = (v2-v1) if isinstance(v1,(int,float)) else "-"
    cols[i].metric(lab, v2, f"{delta:+}" if delta!="- " else "")
