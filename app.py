import streamlit as st
import calendar
from datetime import date
from fpdf import FPDF

st.set_page_config(layout="wide")

# Inicialización
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "disp_m":[], "disp_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {}

st.title("🗓️ Planificador de Turnos con Reportes")

fecha_sel = st.date_input("Mes", date(2026, 6, 1))
anio, mes = fecha_sel.year, fecha_sel.month
_, num_dias = calendar.monthrange(anio, mes)

# --- RESUMEN DE TURNOS ---
st.subheader("📊 Resumen de Turnos")
resumen = {n: {'M': 0, 'T': 0} for n in st.session_state.agentes}
for (d, t), nombre in st.session_state.grilla.items():
    if nombre in resumen:
        resumen[nombre][t] += 1

cols_res = st.columns(len(st.session_state.agentes))
for i, n in enumerate(st.session_state.agentes):
    cols_res[i].metric(n, f"M: {resumen[n]['M']} | T: {resumen[n]['T']}")

# --- LÓGICA DE EXPORTACIÓN PDF ---
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Planilla de Turnos {mes}/{anio}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    for d in range(1, num_dias + 1):
        m = st.session_state.grilla.get((d, 'M'), "-")
        t = st.session_state.grilla.get((d, 'T'), "-")
        pdf.cell(200, 8, txt=f"Dia {d}: Manana: {m} | Tarde: {t}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

st.sidebar.download_button(
    label="📥 Descargar PDF",
    data=generar_pdf(),
    file_name="planilla_turnos.pdf",
    mime="application/pdf"
)

# [MANTENER AQUÍ EL RESTO DEL CÓDIGO ANTERIOR: MENU SIDEBAR, MOTOR AUTOCOMPLETAR Y PLANILLA]
# (Pega aquí la sección 2, 3 y 4 del código anterior que ya te funcionaba)
