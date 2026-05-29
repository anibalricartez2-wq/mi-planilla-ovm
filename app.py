import streamlit as st
import calendar
from datetime import date
from fpdf import FPDF

st.set_page_config(layout="wide")

# 1. ESTADO INICIAL
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {}

st.title("🗓️ Planificador con Equidad Primero")

fecha_sel = st.date_input("Seleccionar mes", date(2026, 6, 1))
anio, mes = fecha_sel.year, fecha_sel.month
_, num_dias = calendar.monthrange(anio, mes)

with st.sidebar:
    limite_horas = st.number_input("Límite horas", value=130)
    horas_turno = st.number_input("Horas por turno", value=6.5)
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Mañana", range(1, num_dias+1), key=f"dm_{n}")
            st.session_state.prefs[n]['pref_t'] = st.multiselect("Tarde", range(1, num_dias+1), key=f"dt_{n}")
            st.session_state.prefs[n]['bloq'] = st.multiselect("NO trabajar", range(1, num_dias+1), key=f"bl_{n}")

# 2. MOTOR: Equidad primero (baja carga) -> Restricciones después
def ejecutar_autocompletado():
    temp_grilla = {}
    turnos_acumulados = {n: 0 for n in st.session_state.agentes}
    
    for d in range(1, num_dias + 1):
        for t in ['M', 'T']:
            # Ordenar agentes por carga de trabajo (Equidad)
            agentes_ordenados = sorted(st.session_state.agentes, key=lambda n: turnos_acumulados[n])
            
            # Seleccionar candidato apto (no bloqueado y con cupo de horas)
            candidato_elegido = None
            for n in agentes_ordenados:
                if d not in st.session_state.prefs[n]['bloq']:
                    if (turnos_acumulados[n] + 1) * horas_turno <= limite_horas:
                        candidato_elegido = n
                        break
            
            if candidato_elegido:
                temp_grilla[(d, t)] = candidato_elegido
                turnos_acumulados[candidato_elegido] += 1
    st.session_state.grilla = temp_grilla

if st.sidebar.button("🚀 Autocompletar"):
    ejecutar_autocompletado()
    st.rerun()

# 3. PDF CORREGIDO
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Planilla {mes}/{anio}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    for d in range(1, num_dias + 1):
        m = st.session_state.grilla.get((d, 'M'), "-")
        t = st.session_state.grilla.get((d, 'T'), "-")
        pdf.cell(200, 8, txt=f"Dia {d}: M: {m} | T: {t}", ln=True)
    # Corrección: output(dest='S') devuelve string, .encode('latin-1') lo hace bytes
    return pdf.output(dest='S').encode('latin-1')

st.sidebar.download_button("📥 Descargar PDF", data=generar_pdf(), file_name="planilla.pdf", mime="application/pdf")

# 4. PLANILLA
for d in range(1, num_dias + 1):
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d}**")
    val_m = st.session_state.grilla.get((d, 'M'), "")
    val_t = st.session_state.grilla.get((d, 'T'), "")
    
    op = [""] + st.session_state.agentes
    st.session_state.grilla[(d, 'M')] = c2.selectbox(f"M {d}", op, index=op.index(val_m) if val_m in op else 0, key=f"M_{d}")
    st.session_state.grilla[(d, 'T')] = c3.selectbox(f"T {d}", op, index=op.index(val_t) if val_t in op else 0, key=f"T_{d}")

if st.sidebar.button("🗑️ Limpiar"):
    st.session_state.grilla = {}
    st.rerun()
