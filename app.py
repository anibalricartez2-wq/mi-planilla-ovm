import streamlit as st

st.set_page_config(layout="wide")

# 1. ESTADO INICIAL
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {}

st.title("🗓️ Planificador - Motor de Asignación")

# 2. MENU DE RESTRICCIONES
with st.sidebar:
    st.header("Restricciones")
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Mañana (Día)", range(1, 32), key=f"dm_{n}")
            st.session_state.prefs[n]['bloq'] = st.multiselect("NO trabajar", range(1, 32), key=f"bl_{n}")

# 3. MOTOR DE AUTOCOMPLETADO
if st.sidebar.button("🚀 Autocompletar"):
    st.session_state.grilla = {}
    for d in range(1, 32):
        for t in ['M', 'T']:
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            
            def criterio(n):
                es_pref = 0 if d in (st.session_state.prefs[n]['pref_m'] if t == 'M' else []) else 1
                turnos = sum(1 for k, v in st.session_state.grilla.items() if v == n)
                return (es_pref, turnos)
            
            cands.sort(key=criterio)
            if cands:
                st.session_state.grilla[(d, t)] = cands[0]
    st.rerun()

# 4. PLANILLA
st.write("---")
for d in range(1, 32):
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d}**")
    
    # Valores actuales
    m_val = st.session_state.grilla.get((d, 'M'), "")
    t_val = st.session_state.grilla.get((d, 'T'), "")
    
    # Selectbox con clave única y limpia
    st.session_state.grilla[(d, 'M')] = c2.selectbox(
        f"M {d}", [""] + st.session_state.agentes, 
        index=([""] + st.session_state.agentes).index(m_val) if m_val in [""] + st.session_state.agentes else 0,
        key=f"Sel_M_{d}"
    )
    
    st.session_state.grilla[(d, 'T')] = c3.selectbox(
        f"T {d}", [""] + st.session_state.agentes, 
        index=([""] + st.session_state.agentes).index(t_val) if t_val in [""] + st.session_state.agentes else 0,
        key=f"Sel_T_{d}"
    )

if st.sidebar.button("🗑️ Limpiar"):
    st.session_state.grilla = {}
    st.rerun()
