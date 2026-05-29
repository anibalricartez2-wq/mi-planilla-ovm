import streamlit as st
import calendar
from datetime import date

st.set_page_config(layout="wide")

# 1. ESTADO INICIAL
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {}

st.title("🗓️ Planificador de Turnos")

# 2. CONFIGURACIÓN SIDEBAR
with st.sidebar:
    st.header("Restricciones")
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Días (M)", range(1, 32), key=f"dm_{n}")
            st.session_state.prefs[n]['pref_t'] = st.multiselect("Días (T)", range(1, 32), key=f"dt_{n}")
            st.session_state.prefs[n]['bloq'] = st.multiselect("NO trabajar", range(1, 32), key=f"bl_{n}")

# 3. MOTOR DE AUTOCOMPLETADO (La versión que sí funcionó)
def ejecutar_autocompletado():
    temp_grilla = {}
    for d in range(1, 32):
        for t in ['M', 'T']:
            # Candidatos: los que no están bloqueados
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            
            # Ordenar por: Preferencia (0) > Equidad (suma de turnos previos)
            cands.sort(key=lambda n: (
                0 if d in (st.session_state.prefs[n]['pref_m'] if t == 'M' else st.session_state.prefs[n]['pref_t']) else 1,
                sum(1 for k, v in temp_grilla.items() if v == n)
            ))
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
    # Calculamos día de semana para Junio 2026 (fijo para que no rompa el motor)
    dia_idx = date(2026, 6, d).weekday()
    dia_str = dias_semana_nombres[dia_idx]
    
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d} ({dia_str})**")
    
    # Selectbox simple usando las claves para refrescar
    m_choice = c2.selectbox(f"M {d}", [""] + st.session_state.agentes, key=f"M_{d}")
    t_choice = c3.selectbox(f"T {d}", [""] + st.session_state.agentes, key=f"T_{d}")
    
    # Actualizar estado
    st.session_state.grilla[(d, 'M')] = m_choice
    st.session_state.grilla[(d, 'T')] = t_choice

if st.sidebar.button("🗑️ Limpiar"):
    st.session_state.grilla = {}
    st.rerun()
