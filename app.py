import streamlit as st

st.set_page_config(layout="wide")

# 1. ESTADO INICIAL
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    # Estructura completa de preferencias
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "disp_m":[], "disp_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {}

st.title("🗓️ Planificador de Turnos - Configuración Completa")

# 2. MENU SIDEBAR (Con todas las restricciones)
with st.sidebar:
    st.header("Restricciones")
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.write("**Días Exactos (Mes)**")
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Mañana", range(1, 32), key=f"dm_{n}")
            st.session_state.prefs[n]['pref_t'] = st.multiselect("Tarde", range(1, 32), key=f"dt_{n}")
            st.write("**Semanal (Lu-Do)**")
            st.session_state.prefs[n]['disp_m'] = st.multiselect("Semanal Mañana", ["Lu","Ma","Mi","Ju","Vi","Sá","Do"], key=f"sm_{n}")
            st.session_state.prefs[n]['disp_t'] = st.multiselect("Semanal Tarde", ["Lu","Ma","Mi","Ju","Vi","Sá","Do"], key=f"st_{n}")
            st.write("**Bloqueos**")
            st.session_state.prefs[n]['bloq'] = st.multiselect("NO trabajar", range(1, 32), key=f"bl_{n}")

# 3. MOTOR DE AUTOCOMPLETADO
def ejecutar_autocompletado():
    dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
    temp_grilla = {}
    
    for d in range(1, 32):
        # Asumimos una lógica simple de día de la semana (1 es lunes)
        dia_nombre = dias_semana[ (d-1) % 7 ]
        
        for t in ['M', 'T']:
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            
            # Ordenar por: Preferencia Exacta > Preferencia Semanal > Equidad
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

# 4. PLANILLA (Visualización)
st.write("---")
for d in range(1, 32):
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d}**")
    
    # FORZAMOS el valor del selectbox usando el estado de grilla
    m_val = st.session_state.grilla.get((d, 'M'), "")
    t_val = st.session_state.grilla.get((d, 'T'), "")
    
    # El truco para que actualice: usar 'index' con lógica de lista
    opts = [""] + st.session_state.agentes
    
    m_choice = c2.selectbox(f"M {d}", opts, index=opts.index(m_val) if m_val in opts else 0, key=f"M_{d}")
    t_choice = c3.selectbox(f"T {d}", opts, index=opts.index(t_val) if t_val in opts else 0, key=f"T_{d}")
    
    st.session_state.grilla[(d, 'M')] = m_choice
    st.session_state.grilla[(d, 'T')] = t_choice

if st.sidebar.button("🗑️ Limpiar"):
    st.session_state.grilla = {}
    st.rerun()
