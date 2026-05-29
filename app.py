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

st.title("🗓️ Planificador de Turnos con Límite Variable")

# Configuración de fecha y límite global
fecha_sel = st.date_input("Seleccionar mes", date(2026, 6, 1))
anio, mes = fecha_sel.year, fecha_sel.month
_, num_dias = calendar.monthrange(anio, mes)

# 2. MENU SIDEBAR (Con límite de horas ajustable)
with st.sidebar:
    st.header("Configuración")
    limite_horas = st.number_input("Límite horas mensuales", value=130, step=1)
    horas_por_turno = st.number_input("Horas por turno", value=6.5, step=0.5)
    
    st.header("Restricciones")
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Mañana (Día)", range(1, num_dias+1), key=f"dm_{n}")
            st.session_state.prefs[n]['pref_t'] = st.multiselect("Tarde (Día)", range(1, num_dias+1), key=f"dt_{n}")
            st.session_state.prefs[n]['bloq'] = st.multiselect("NO trabajar", range(1, num_dias+1), key=f"bl_{n}")

# 3. MOTOR CON LÍMITE DINÁMICO
def ejecutar_autocompletado():
    temp_grilla = {}
    turnos_acumulados = {n: 0 for n in st.session_state.agentes}
    
    for d in range(1, num_dias + 1):
        for t in ['M', 'T']:
            # Filtro: no bloqueado Y no exceder límite
            cands = [n for n in st.session_state.agentes 
                     if d not in st.session_state.prefs[n]['bloq'] 
                     and (turnos_acumulados[n] + 1) * horas_por_turno <= limite_horas]
            
            # Orden: Preferencia exacta > Equidad
            cands.sort(key=lambda n: (
                0 if d in (st.session_state.prefs[n]['pref_m'] if t == 'M' else st.session_state.prefs[n]['pref_t']) else 1,
                turnos_acumulados[n]
            ))
            
            if cands:
                asignado = cands[0]
                temp_grilla[(d, t)] = asignado
                turnos_acumulados[asignado] += 1
    st.session_state.grilla = temp_grilla

if st.sidebar.button("🚀 Autocompletar"):
    ejecutar_autocompletado()
    st.rerun()

# 4. RESUMEN Y PLANILLA
st.subheader(f"📊 Resumen (Límite: {limite_horas} hs)")
resumen = {n: {'M': 0, 'T': 0} for n in st.session_state.agentes}
for (d, t), nombre in st.session_state.grilla.items():
    if nombre in resumen: resumen[nombre][t] += 1

cols_res = st.columns(len(st.session_state.agentes))
for i, n in enumerate(st.session_state.agentes):
    total_horas = (resumen[n]['M'] + resumen[n]['T']) * horas_por_turno
    cols_res[i].metric(n, f"{total_horas} hs", f"M:{resumen[n]['M']} T:{resumen[n]['T']}")

# 5. EXPORTAR PDF
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Planilla {mes}/{anio} - Limite: {limite_horas}hs", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    for d in range(1, num_dias + 1):
        m = st.session_state.grilla.get((d, 'M'), "-")
        t = st.session_state.grilla.get((d, 'T'), "-")
        pdf.cell(200, 8, txt=f"Dia {d}: M: {m} | T: {t}", ln=True)
    return pdf.output(dest='S')

st.sidebar.download_button("📥 Descargar PDF", data=generar_pdf(), file_name="planilla.pdf", mime="application/pdf")

# Render planilla
for d in range(1, num_dias + 1):
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d}**")
    val_m = st.session_state.grilla.get((d, 'M'), "")
    val_t = st.session_state.grilla.get((d, 'T'), "")
    
    opciones = [""] + st.session_state.agentes
    st.session_state.grilla[(d, 'M')] = c2.selectbox(f"M {d}", opciones, index=opciones.index(val_m) if val_m in opciones else 0, key=f"M_{d}")
    st.session_state.grilla[(d, 'T')] = c3.selectbox(f"T {d}", opciones, index=opciones.index(val_t) if val_t in opciones else 0, key=f"T_{d}")

if st.sidebar.button("🗑️ Limpiar"):
    st.session_state.grilla = {}
    st.rerun()
