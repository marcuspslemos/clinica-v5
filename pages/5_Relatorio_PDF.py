import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from datetime import datetime

# ---------------------------
# 1) Carregar e filtrar dados
# ---------------------------
st.set_page_config(page_title="Relatório PDF", page_icon="📄", layout="wide")
st.title("📄 Gerar Relatório em PDF")

df = pd.read_csv("data/dados_ficticios.csv")
df["Data"] = pd.to_datetime(df["Data"])

col1, col2 = st.columns(2)
data_ini = col1.date_input("Data inicial", df["Data"].min().date())
data_fim = col2.date_input("Data final", df["Data"].max().date())

df_f = df[(df["Data"] >= pd.to_datetime(data_ini)) & (df["Data"] <= pd.to_datetime(data_fim))]
df_real = df_f[df_f["Status"] == "Realizada"]
df_cancel = df_f[df_f["Status"] == "Cancelada"]

# ---------------------------
# 2) KPIs principais
# ---------------------------
atendimentos = len(df_real)
faturamento = float(df_real["Valor"].sum()) if not df_real.empty else 0.0
ocupacao = (len(df_f[df_f["Ocupada"] == "Sim"]) / len(df_f) * 100) if len(df_f) else 0.0
cancelamentos = len(df_cancel)
top_prof = df_real["Profissional"].value_counts().idxmax() if not df_real.empty else "-"

kpi_cols = st.columns(5)
kpi_cols[0].metric("Atendimentos", f"{atendimentos}")
kpi_cols[1].metric("Faturamento", f"R$ {faturamento:,.2f}")
kpi_cols[2].metric("Ocupação", f"{ocupacao:.1f}%")
kpi_cols[3].metric("Cancelamentos", f"{cancelamentos}")
kpi_cols[4].metric("Top Profissional", top_prof)

st.markdown("---")

# ---------------------------
# 3) Gráficos (Plotly)
# ---------------------------
# 3.1 Evolução de atendimentos
evo = df_real.groupby("Data").size().reset_index(name="Total")
fig_evo = px.line(
    evo, x="Data", y="Total", markers=True,
    color_discrete_sequence=["#b71c1c"],
    title="Evolução de Atendimentos"
)

# 3.2 Receita por convênio
por_plano = df_real.groupby("Plano")["Valor"].sum().reset_index().sort_values("Valor", ascending=False)
fig_plano = px.bar(
    por_plano, x="Plano", y="Valor", text_auto=True,
    color_discrete_sequence=px.colors.sequential.Reds,
    title="Faturamento por Convênio"
)

# Render na página
st.plotly_chart(fig_evo, use_container_width=True)
st.plotly_chart(fig_plano, use_container_width=True)

# ---------------------------
# 4) Exportar gráficos como PNG (em memória)
# ---------------------------
img_buf_evo = BytesIO()
img_buf_plano = BytesIO()
fig_evo.write_image(img_buf_evo, format="png", scale=2)   # requer kaleido
fig_plano.write_image(img_buf_plano, format="png", scale=2)
img_buf_evo.seek(0)
img_buf_plano.seek(0)

# ---------------------------
# 5) Montar PDF (ReportLab)
# ---------------------------
def gerar_pdf():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    # Cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, h - 2*cm, "Relatório Mensal – Clínica de Psicologia")
    c.setFont("Helvetica", 10)
    periodo_txt = f"Período: {data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M')
    c.drawString(2*cm, h - 2.6*cm, periodo_txt)
    c.drawString(2*cm, h - 3.0*cm, f"Gerado em: {data_geracao}")

    # KPIs
    y = h - 4.2*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "KPIs Principais")
    c.setFont("Helvetica", 11)
    y -= 0.8*cm
    kpis = [
        f"Atendimentos: {atendimentos}",
        f"Faturamento: R$ {faturamento:,.2f}",
        f"Ocupação: {ocupacao:.1f}%",
        f"Cancelamentos: {cancelamentos}",
        f"Top Profissional: {top_prof}"
    ]
    for item in kpis:
        c.drawString(2*cm, y, f"• {item}")
        y -= 0.6*cm

    # Gráfico 1: Evolução
    y_img = y - 0.6*cm
    evo_img = ImageReader(img_buf_evo)
    img_w = w - 4*cm
    img_h = 7*cm
    c.drawImage(evo_img, 2*cm, y_img - img_h, width=img_w, height=img_h, preserveAspectRatio=True, mask='auto')

    # Quebra de página para o segundo gráfico
    c.showPage()

    # Cabeçalho da página 2
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, h - 2*cm, "Análises Financeiras")

    # Gráfico 2: Convênios
    plano_img = ImageReader(img_buf_plano)
    c.drawImage(plano_img, 2*cm, h - 10*cm, width=img_w, height=7*cm, preserveAspectRatio=True, mask='auto')

    # Insights textuais (exemplo)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, h - 11.2*cm, "Resumo/Insights")
    c.setFont("Helvetica", 11)
    insights = [
        f"• Pico de atendimentos nos dias de maior movimento (ver evolução).",
        f"• Convênio líder de receita: {por_plano.iloc[0]['Plano'] if not por_plano.empty else '-'}",
        f"• Reduzindo cancelamentos em 20%, potencial de +R$ {0.2*cancelamentos* (df_real['Valor'].mean() if not df_real.empty else 0):,.2f}/mês.",
    ]
    y_ins = h - 12.0*cm
    for t in insights:
        c.drawString(2*cm, y_ins, t)
        y_ins -= 0.7*cm

    c.showPage()
    c.save()
    buf.seek(0)
    return buf

# ---------------------------
# 6) Botão de download
# ---------------------------
pdf_buffer = gerar_pdf()
st.download_button(
    label="📥 Baixar Relatório PDF",
    data=pdf_buffer,
    file_name=f"relatorio_clinica_{data_ini.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf",
    mime="application/pdf"
)
