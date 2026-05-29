import streamlit as st
import calendar
from datetime import date

st.set_page_config(layout="wide")

# 1. ESTADO INICIAL
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "disp_m":[], "disp_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {}

# Configuración de fechas
anio, mes = 2026, 6
_, num_dias = calendar.monthrange(anio, mes)

st.title(f"🗓️ Planificador - Junio 2026 ({num_dias} días)")

# 2. MENU SIDEBAR
with st.sidebar:
    st.header("Restricciones")
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Mañana (Día)", range(1, num_dias+1), key=f"dm_{n}")
            st.session_state.prefs[n]['pref_t'] = st.multiselect("Tarde (Día)", range(1, num_dias+1), key=f"dt_{n}")
            st.session_state.prefs[n]['disp_m'] = st.multiselect("Semanal Mañana", ["Lu","Ma","Mi","Ju","Vi","Sá","Do"], key=f"sm_{n}")
            st.session_state.prefs[n]['disp_t'] = st.multiselect("Semanal Tarde", ["Lu","Ma","Mi","Ju","Vi","Sá","Do"], key=f"st_{n}")
            st.session_state.prefs[n]['bloq'] = st.multiselect("NO trabajar", range(1, num_dias+1), key=f"bl_{n}")

# 3. MOTOR DE AUTOCOMPLETADO
def ejecutar_autocompletado():
    dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
    temp_grilla = {}
    
    for d in range(1, num_dias + 1):
        dia_nombre = dias_semana[date(anio, mes, d).weekday()]
        for t in ['M', 'T']:
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            
            cands.sort(key=lambda n: (
                0 if d in (st.session_state.prefs[n]['pref_m'] if t == 'M' else st.session_state.prefs[n]['pref_t']) else 1,
                0 if dia_nombre in (st.session_state.prefs[n]['disp_m'] if t == 'M' else st.session_state.prefs[n]['disp_t']) else 1,
                sum(1 for k, v in temp_grilla.items() if v == n)
            ))
            if cands:
                temp_grilla[(d, t)] = cands[0]
    st.session_state.grilla = temp_grilla

if st.sidebar.button("🚀 Autocompletar"):
    ejecutar_autocompletado()
    st.rerun()

# 4. PLANILLA
st.write("---")
dias_semana_nombres = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]

for d in range(1, num_dias + 1):
    dia_str = dias_semana_nombres[date(anio, mes, d).weekday()]
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d} ({dia_str})**")
    
    # Asignación manual
    m_choice = c2.selectbox(f"M {d}", [""] + st.session_state.agentes, key=f"M_{d}")
    t_choice = c3.selectbox(f"T {d}", [""] + st.session_state.agentes, key=f"T_{d}")
    
    st.session_state.grilla[(d, 'M')] = m_choice
    st.session_state.grilla[(d, 'T')] = t_choice

if st.sidebar.button("🗑️ Limpiar"):
    st.session_state.grilla = {}
    st.rerun()
