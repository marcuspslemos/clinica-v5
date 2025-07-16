import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comparativo de Períodos", page_icon="🆚", layout="wide")
st.title("🆚 Comparativo entre Períodos")

# 1) Carrega dados
df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])

# 2) Seletor de dois intervalos
p1 = st.date_input("📅 Período 1 (início, fim)", [df.Data.min(), df.Data.min() + pd.Timedelta(days=7)], key="cp1")
p2 = st.date_input("📅 Período 2 (início, fim)", [df.Data.min() + pd.Timedelta(days=8), df.Data.max()], key="cp2")

# 3) Função que extrai KPIs
def get_metrics(sub):
    feitos   = sub[sub.Status == "Realizada"]
    cancel   = sub[sub.Status == "Cancelada"]
    top_prof = feitos.Profissional.value_counts().idxmax() if not feitos.empty else "-"
    return {
        "Atendimentos": len(feitos),
        "Faturamento":  feitos.Valor.sum(),
        "Cancelamentos": len(cancel),
        "Top Profissional": top_prof
    }

# 4) Aplica aos períodos
df1 = df[(df.Data >= p1[0]) & (df.Data <= p1[1])]
df2 = df[(df.Data >= p2[0]) & (df.Data <= p2[1])]
m1, m2 = get_metrics(df1), get_metrics(df2)

# 5) Exibe em métricas lado a lado
labels = ["Atendimentos","Faturamento","Cancelamentos","Top Profissional"]
cols = st.columns(4)
for i, lab in enumerate(labels):
    val1, val2 = m1[lab], m2[lab]
    delta = val2 - val1 if isinstance(val1, (int,float)) else None
    cols[i].metric(
        label=lab,
        value=f"{val2:,}" if isinstance(val2,(int,float)) else val2,
        delta=f"{delta:+,}" if isinstance(delta,(int,float)) else ""
    )
