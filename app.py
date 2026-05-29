import streamlit as st
import calendar
from datetime import date

st.set_page_config(layout="wide")

# 1. ESTADO INICIAL
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "disp_m":[], "disp_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {} 

st.title("🗓️ Planificador con Calendario")

# Configuración de fecha (Junio 2026)
anio, mes = 2026, 6
dias_mes = calendar.monthrange(anio, mes)[1]
dias_semana_nombres = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]

# 2. MENU DE RESTRICCIONES
with st.sidebar:
    st.header("Configuración")
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Días (M)", range(1, dias_mes+1), key=f"dm_{n}")
            st.session_state.prefs[n]['disp_m'] = st.multiselect("Semanal (M)", dias_semana_nombres, key=f"sm_{n}")
            st.session_state.prefs[n]['bloq'] = st.multiselect("Días NO trabajar", range(1, dias_mes+1), key=f"bl_{n}")

# 3. MOTOR DE AUTOCOMPLETADO
def autocompletar():
    st.session_state.grilla = {}
    for d in range(1, dias_mes + 1):
        # Calcular qué día de la semana cae el día 'd' de Junio 2026
        dia_semana_idx = date(anio, mes, d).weekday()
        dia_nombre = dias_semana_nombres[dia_semana_idx]
        
        for t in ['M', 'T']:
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            
            def criterio(n):
                # Prioridad 1: Día exacto, Prioridad 2: Día semanal, Prioridad 3: Equidad
                p1 = 0 if d in (st.session_state.prefs[n]['pref_m'] if t == 'M' else st.session_state.prefs[n]['pref_t']) else 1
                p2 = 0 if dia_nombre in (st.session_state.prefs[n]['disp_m'] if t == 'M' else st.session_state.prefs[n]['disp_t']) else 1
                turnos = sum(1 for k, v in st.session_state.grilla.items() if v == n)
                return (p1, p2, turnos)
            
            cands.sort(key=criterio)
            if cands:
                st.session_state.grilla[(d, t)] = cands[0]

if st.sidebar.button("🚀 Autocompletar"):
    autocompletar()
    st.rerun()

# 4. INTERFAZ CON DIAS DE LA SEMANA
st.write("---")
for d in range(1, dias_mes + 1):
    dia_semana_idx = date(anio, mes, d).weekday()
    dia_str = dias_semana_nombres[dia_semana_idx]
    
    # Marcamos en rojo los fines de semana (Sá/Do) para visibilidad
    color = "red" if dia_semana_idx >= 5 else "black"
    
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.markdown(f"**Día {d} (<span style='color:{color}'>{dia_str}</span>)**", unsafe_allow_html=True)
    
    m_val = st.session_state.grilla.get((d, 'M'), "")
    t_val = st.session_state.grilla.get((d, 'T'), "")
    
    st.session_state.grilla[(d, 'M')] = c2.selectbox(f"M {d}", [""] + st.session_state.agentes, 
                                                    key=f"M_{d}", index=0 if m_val=="" else st.session_state.agentes.index(m_val)+1)
    st.session_state.grilla[(d, 'T')] = c3.selectbox(f"T {d}", [""] + st.session_state.agentes, 
                                                    key=f"T_{d}", index=0 if t_val=="" else st.session_state.agentes.index(t_val)+1)
