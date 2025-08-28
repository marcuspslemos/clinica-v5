import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from datetime import datetime

# Fallback para exportação de imagens
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

st.set_page_config(page_title="Relatório PDF", page_icon="📄", layout="wide")
st.title("📄 Gerar Relatório em PDF")

# ---------------------------
# 1) Carregar e filtrar dados
# ---------------------------
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
# 3) Gráficos (Plotly) - para visualização
# ---------------------------
evo = df_real.groupby("Data").size().reset_index(name="Total")
fig_evo = px.line(
    evo, x="Data", y="Total", markers=True,
    color_discrete_sequence=["#b71c1c"],
    title="Evolução de Atendimentos"
)

por_plano = df_real.groupby("Plano")["Valor"].sum().reset_index().sort_values("Valor", ascending=False)
fig_plano = px.bar(
    por_plano, x="Plano", y="Valor", text_auto=True,
    color_discrete_sequence=px.colors.sequential.Reds,
    title="Faturamento por Convênio"
)

st.plotly_chart(fig_evo, use_container_width=True)
st.plotly_chart(fig_plano, use_container_width=True)

# ---------------------------
# 4) Funções de exportação
# ---------------------------
def plotly_to_png_bytes(fig, scale=2):
    """
    Tenta exportar a figura Plotly com Kaleido.
    Se falhar (Chromium ausente), levanta RuntimeError.
    """
    buf = BytesIO()
    # Pode lançar RuntimeError no Streamlit Cloud (Chromium não disponível)
    fig.write_image(buf, format="png", scale=scale)
    buf.seek(0)
    return buf

def line_matplotlib_png_bytes(df_line, xcol, ycol, title):
    """
    Gera PNG (line chart) com Matplotlib como fallback.
    """
    buf = BytesIO()
    plt.figure(figsize=(8, 3))
    plt.plot(df_line[xcol], df_line[ycol], marker="o")
    plt.title(title)
    plt.xlabel(xcol)
    plt.ylabel(ycol)
    plt.grid(True, alpha=0.3)
    # eixo de data amigável
    if pd.api.types.is_datetime64_any_dtype(df_line[xcol]):
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gca().xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=180)
    plt.close()
    buf.seek(0)
    return buf

def bar_matplotlib_png_bytes(df_bar, xcol, ycol, title):
    """
    Gera PNG (bar chart) com Matplotlib como fallback.
    """
    buf = BytesIO()
    plt.figure(figsize=(8, 3))
    plt.bar(df_bar[xcol], df_bar[ycol])
    plt.title(title)
    plt.xlabel(xcol)
    plt.ylabel(ycol)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=180)
    plt.close()
    buf.seek(0)
    return buf

# ---------------------------
# 5) Exportar gráficos como PNG (com fallback)
# ---------------------------
# Evolução
try:
    img_buf_evo = plotly_to_png_bytes(fig_evo, scale=2)
except Exception:
    img_buf_evo = line_matplotlib_png_bytes(evo, "Data", "Total", "Evolução de Atendimentos")

# Convênios
try:
    img_buf_plano = plotly_to_png_bytes(fig_plano, scale=2)
except Exception:
    img_buf_plano = bar_matplotlib_png_bytes(por_plano, "Plano", "Valor", "Faturamento por Convênio")

# ---------------------------
# 6) Montar PDF (ReportLab)
# ---------------------------
def gerar_pdf():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    # Cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, h - 2*cm, "Relatório Mensal – Clínica de Psicologia")
    c.setFont("Helvetica", 10)
    periodo_txt = f"Período: {pd.to_datetime(data_ini).strftime('%d/%m/%Y')} a {pd.to_datetime(data_fim).strftime('%d/%m/%Y')}"
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

    # Quebra de página
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
    media_ticket = float(df_real["Valor"].mean()) if not df_real.empty else 0.0
    insights = [
        "• Pico de atendimentos e sazonalidades observadas na evolução.",
        f"• Convênio líder de receita: {por_plano.iloc[0]['Plano'] if not por_plano.empty else '-'}",
        f"• Reduzindo cancelamentos em 20%, potencial de +R$ {0.2*cancelamentos*media_ticket:,.2f}/mês.",
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
# 7) Botão de download
# ---------------------------
pdf_buffer = gerar_pdf()
st.download_button(
    label="📥 Baixar Relatório PDF",
    data=pdf_buffer,
    file_name=f"relatorio_clinica_{pd.to_datetime(data_ini).strftime('%Y%m%d')}_{pd.to_datetime(data_fim).strftime('%Y%m%d')}.pdf",
    mime="application/pdf"
)
