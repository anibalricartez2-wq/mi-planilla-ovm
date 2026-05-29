import streamlit as st
import calendar
from datetime import date

st.set_page_config(layout="wide")

# 1. ESTADO INICIAL
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "disp_m":[], "disp_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {} 

st.title("🗓️ Planificador de Turnos - Autocompletado Garantizado")

anio, mes = 2026, 6
dias_mes = calendar.monthrange(anio, mes)[1]
dias_semana_nombres = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]

# 2. MENU DE RESTRICCIONES
with st.sidebar:
    st.header("Restricciones")
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.write("**Días Exactos**")
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Mañana", range(1, dias_mes+1), key=f"dm_{n}")
            st.session_state.prefs[n]['pref_t'] = st.multiselect("Tarde", range(1, dias_mes+1), key=f"dt_{n}")
            st.write("**Semanal (Lu-Do)**")
            st.session_state.prefs[n]['disp_m'] = st.multiselect("Semanal Mañana", dias_semana_nombres, key=f"sm_{n}")
            st.session_state.prefs[n]['disp_t'] = st.multiselect("Semanal Tarde", dias_semana_nombres, key=f"st_{n}")
            st.write("**Bloqueos**")
            st.session_state.prefs[n]['bloq'] = st.multiselect("Días NO trabajar", range(1, dias_mes+1), key=f"bl_{n}")

# 3. MOTOR DE AUTOCOMPLETADO
def autocompletar():
    st.session_state.grilla = {}
    for d in range(1, dias_mes + 1):
        dia_nombre = dias_semana_nombres[date(anio, mes, d).weekday()]
        
        for t in ['M', 'T']:
            # Candidatos: Todos menos los que están bloqueados
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            
            if not cands: continue
            
            # Ordenar candidatos
            def criterio(n):
                prefs = st.session_state.prefs[n]
                # P1: Preferencia exacta (0 mejor que 1)
                es_pref_exacta = 0 if d in (prefs['pref_m'] if t == 'M' else prefs['pref_t']) else 1
                # P2: Preferencia semanal (0 mejor que 1)
                es_pref_sem = 0 if dia_nombre in (prefs['disp_m'] if t == 'M' else prefs['disp_t']) else 1
                # P3: Equidad (cuenta turnos asignados hasta ahora)
                turnos = sum(1 for k, v in st.session_state.grilla.items() if v == n)
                return (es_pref_exacta, es_pref_sem, turnos)
            
            cands.sort(key=criterio)
            # Asignación forzada
            st.session_state.grilla[(d, t)] = cands[0]

if st.sidebar.button("🚀 Autocompletar"):
    autocompletar()
    st.rerun()

# 4. INTERFAZ
st.write("---")
for d in range(1, dias_mes + 1):
    dia_str = dias_semana_nombres[date(anio, mes, d).weekday()]
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d} ({dia_str})**")
    
    m_val = st.session_state.grilla.get((d, 'M'), "")
    t_val = st.session_state.grilla.get((d, 'T'), "")
    
    st.session_state.grilla[(d, 'M')] = c2.selectbox(f"M {d}", [""] + st.session_state.agentes, 
                                                    key=f"M_{d}", index=0 if m_val=="" else st.session_state.agentes.index(m_val)+1)
    st.session_state.grilla[(d, 'T')] = c3.selectbox(f"T {d}", [""] + st.session_state.agentes, 
                                                    key=f"T_{d}", index=0 if t_val=="" else st.session_state.agentes.index(t_val)+1)

if st.sidebar.button("🗑️ Limpiar Planilla"):
    st.session_state.grilla = {}
    st.rerun()
