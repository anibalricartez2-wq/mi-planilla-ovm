import streamlit as st

st.set_page_config(layout="wide")

# 1. ESTADO INICIAL
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {}

st.title("🗓️ Planificador de Turnos")

# 2. MENU SIDEBAR (Se renderiza siempre primero)
with st.sidebar:
    st.header("Configuración")
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Días (Mañana)", range(1, 32), key=f"dm_{n}")
            st.session_state.prefs[n]['pref_t'] = st.multiselect("Días (Tarde)", range(1, 32), key=f"dt_{n}")
            st.session_state.prefs[n]['bloq'] = st.multiselect("NO trabajar", range(1, 32), key=f"bl_{n}")

# 3. MOTOR (Separado de la vista)
def ejecutar_autocompletado():
    temp_grilla = {}
    for d in range(1, 32):
        for t in ['M', 'T']:
            # Elegir candidatos
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            
            # Ordenar: Preferencia (0) > Equidad (suma de turnos previos)
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

# 4. PLANILLA (Visualización simple)
st.write("---")
for d in range(1, 32):
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d}**")
    
    # Valores de la grilla
    m_val = st.session_state.grilla.get((d, 'M'), "")
    t_val = st.session_state.grilla.get((d, 'T'), "")
    
    # Selectbox simple
    m_choice = c2.selectbox(f"M {d}", [""] + st.session_state.agentes, key=f"M_{d}")
    t_choice = c3.selectbox(f"T {d}", [""] + st.session_state.agentes, key=f"T_{d}")
    
    # Actualizar estado manualmente si el usuario cambia algo
    st.session_state.grilla[(d, 'M')] = m_choice
    st.session_state.grilla[(d, 'T')] = t_choice

if st.sidebar.button("🗑️ Limpiar"):
    st.session_state.grilla = {}
    st.rerun()
