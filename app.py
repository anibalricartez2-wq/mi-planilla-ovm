import streamlit as st
import calendar
from datetime import date

# Configuración
st.set_page_config(layout="wide")

if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "disp_m":[], "disp_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {}

st.title("🗓️ Planificador - Autocompletado Forzado")

# 1. SIDEBAR
with st.sidebar:
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Mañana (Día)", range(1, 32), key=f"dm_{n}")
            st.session_state.prefs[n]['bloq'] = st.multiselect("NO trabajar", range(1, 32), key=f"bl_{n}")

# 2. BOTÓN DE PROCESO
if st.sidebar.button("🚀 Autocompletar"):
    # Limpiamos y forzamos re-asignación
    st.session_state.grilla = {}
    for d in range(1, 32):
        for t in ['M', 'T']:
            # Elegimos al mejor candidato sin bloqueos
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            
            # Orden: Preferencia exacta > Menos turnos previos
            cands.sort(key=lambda n: (
                0 if d in (st.session_state.prefs[n]['pref_m'] if t == 'M' else st.session_state.prefs[n]['pref_t']) else 1,
                sum(1 for k, v in st.session_state.grilla.items() if v == n)
            ))
            
            if cands:
                st.session_state.grilla[(d, t)] = cands[0]
    st.rerun()

# 3. PLANILLA
st.write("---")
for d in range(1, 32):
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d}**")
    
    # Obtenemos valor actual del diccionario
    m_val = st.session_state.grilla.get((d, 'M'), "")
    t_val = st.session_state.grilla.get((d, 'T'), "")
    
    # Definimos selectbox con el valor actual fijo
    st.session_state.grilla[(d, 'M')] = c2.selectbox(f"M {d}", [""] + st.session_state.agentes, 
                                                    index=([""] + st.session_state.agentes).index(m_val) if m_val in [""] + st.session_state.agentes else 0,
                                                    key=f"M_{d}")
    st.session_state.grilla[(d, 'T')] = c3.selectbox(f"T {d}", [""] + st.session_state.agentes, 
                                                    key=f"T_{d}", index=([""] + st.session_state.agentes).index(t_val) if t_val in [""] + st.session_state.agentes else 0,
                                                    key=f"T_{d}")
