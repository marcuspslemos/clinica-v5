import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Comparativo de Períodos",
    page_icon="🆚",
    layout="wide"
)
st.title("🆚 Comparativo entre Períodos")

# 1) Carrega dados
df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])

# 2) Seletor de dois intervalos
p1 = st.date_input(
    "📅 Período 1 (início, fim)",
    [df.Data.min().date(), df.Data.min().date() + pd.Timedelta(days=7)],
    key="cp1"
)
p2 = st.date_input(
    "📅 Período 2 (início, fim)",
    [df.Data.min().date() + pd.Timedelta(days=8), df.Data.max().date()],
    key="cp2"
)

# Converte cada elemento (datetime.date) para Timestamp
start1, end1 = pd.to_datetime(p1[0]), pd.to_datetime(p1[1])
start2, end2 = pd.to_datetime(p2[0]), pd.to_datetime(p2[1])

# 3) Função para extrair KPIs
def get_metrics(sub):
    feitos = sub[sub.Status == "Realizada"]
    cancel = sub[sub.Status == "Cancelada"]
    top = feitos.Profissional.value_counts().idxmax() if not feitos.empty else "-"
    return {
        "Atendimentos": len(feitos),
        "Faturamento":  feitos.Valor.sum(),
        "Cancelamentos": len(cancel),
        "Top Profissional": top
    }

# 4) Filtra e calcula
df1 = df[(df.Data >= start1) & (df.Data <= end1)]
df2 = df[(df.Data >= start2) & (df.Data <= end2)]
m1, m2 = get_metrics(df1), get_metrics(df2)

# 5) Exibe KPIs lado a lado
labels = ["Atendimentos", "Faturamento", "Cancelamentos", "Top Profissional"]
cols = st.columns(len(labels))
for i, lab in enumerate(labels):
    v1, v2 = m1[lab], m2[lab]
    # delta só para numéricos
    delta = (v2 - v1) if isinstance(v1, (int, float)) else ""
    cols[i].metric(lab, f"{v2:,}" if isinstance(v2, (int, float)) else v2, f"{delta:+,}" if delta!="" else "")
