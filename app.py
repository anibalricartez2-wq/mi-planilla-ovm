import streamlit as st
import calendar
from datetime import date

st.set_page_config(layout="wide")

# 1. ESTADO INICIAL
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "disp_m":[], "disp_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {}

st.title("🗓️ Planificador: Configuración Total")

# 2. MENU SIDEBAR (Restricciones M y T completas)
with st.sidebar:
    st.header("Restricciones")
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.write("--- Días Exactos (Mes) ---")
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Mañana", range(1, 32), key=f"dm_{n}")
            st.session_state.prefs[n]['pref_t'] = st.multiselect("Tarde", range(1, 32), key=f"dt_{n}")
            st.write("--- Semanal (Lu-Do) ---")
            st.session_state.prefs[n]['disp_m'] = st.multiselect("Semanal Mañana", ["Lu","Ma","Mi","Ju","Vi","Sá","Do"], key=f"sm_{n}")
            st.session_state.prefs[n]['disp_t'] = st.multiselect("Semanal Tarde", ["Lu","Ma","Mi","Ju","Vi","Sá","Do"], key=f"st_{n}")
            st.write("--- Bloqueos ---")
            st.session_state.prefs[n]['bloq'] = st.multiselect("Días NO trabajar", range(1, 32), key=f"bl_{n}")

# 3. MOTOR DE AUTOCOMPLETADO
def ejecutar_autocompletado():
    dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
    temp_grilla = {}
    
    for d in range(1, 32):
        dia_nombre = dias_semana[date(2026, 6, d).weekday()]
        for t in ['M', 'T']:
            # Filtro base: no estar bloqueado
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            
            # Orden: 
            # 1. Preferencia exacta (M o T)
            # 2. Preferencia semanal (M o T)
            # 3. Equidad (Turnos totales)
            def criterio(n):
                prefs = st.session_state.prefs[n]
                pref_exacta = 0 if d in (prefs['pref_m'] if t == 'M' else prefs['pref_t']) else 1
                pref_sem = 0 if dia_nombre in (prefs['disp_m'] if t == 'M' else prefs['disp_t']) else 1
                turnos = sum(1 for k, v in temp_grilla.items() if v == n)
                return (pref_exacta, pref_sem, turnos)
            
            cands.sort(key=criterio)
            if cands:
                temp_grilla[(d, t)] = cands[0]
    st.session_state.grilla = temp_grilla

if st.sidebar.button("🚀 Autocompletar"):
    ejecutar_autocompletado()
    st.rerun()

# 4. PLANILLA CON DÍA DE LA SEMANA
st.write("---")
dias_semana_nombres = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]

for d in range(1, 32):
    dia_idx = date(2026, 6, d).weekday()
    dia_str = dias_semana_nombres[dia_idx]
    
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d} ({dia_str})**")
    
    # Asignación manual que respeta el motor
    m_choice = c2.selectbox(f"M {d}", [""] + st.session_state.agentes, key=f"M_{d}")
    t_choice = c3.selectbox(f"T {d}", [""] + st.session_state.agentes, key=f"T_{d}")
    
    st.session_state.grilla[(d, 'M')] = m_choice
    st.session_state.grilla[(d, 'T')] = t_choice

if st.sidebar.button("🗑️ Limpiar"):
    st.session_state.grilla = {}
    st.rerun()
