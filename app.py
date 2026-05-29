import streamlit as st

# Configuración de página
st.set_page_config(layout="wide")

# 1. INICIALIZACIÓN SEGURA (Se ejecuta solo si no existe)
if 'init_done' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {}
    st.session_state.init_done = True

st.title("🗓️ Planificador de Turnos - Gestión Equitativa")

# 2. CONFIGURACIÓN SIDEBAR (Uso de 'key' único y constante)
with st.sidebar:
    st.header("Configuración de Agentes")
    for n in st.session_state.agentes:
        with st.expander(f"Agente: {n}"):
            # Usamos índices temporales para evitar errores de referencia
            st.session_state.prefs[n]['pref_m'] = st.multiselect(
                f"Días exactos (Mañana) - {n}", 
                options=list(range(1, 32)), 
                default=st.session_state.prefs[n]['pref_m'],
                key=f"dm_{n}"
            )
            st.session_state.prefs[n]['bloq'] = st.multiselect(
                f"Días NO trabajar - {n}", 
                options=list(range(1, 32)), 
                default=st.session_state.prefs[n]['bloq'],
                key=f"bl_{n}"
            )

# 3. MOTOR DE AUTOCOMPLETADO
def autocompletar():
    st.session_state.grilla = {}
    dias = range(1, 32)
    
    for d in dias:
        for t in ['M', 'T']:
            # Candidatos que no están bloqueados
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            
            # Ordenar por: 1. Preferencia, 2. Equidad
            def criterio(n):
                es_pref = 0 if d in (st.session_state.prefs[n]['pref_m'] if t == 'M' else st.session_state.prefs[n]['pref_t']) else 1
                turnos_previos = sum(1 for k, v in st.session_state.grilla.items() if v == n)
                return (es_pref, turnos_previos)
            
            cands.sort(key=criterio)
            if cands:
                st.session_state.grilla[(d, t)] = cands[0]

if st.sidebar.button("🚀 Autocompletar"):
    autocompletar()
    st.rerun()

# 4. INTERFAZ DE PLANILLA
for d in range(1, 32):
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d}**")
    
    # Valores guardados
    val_m = st.session_state.grilla.get((d, 'M'), "")
    val_t = st.session_state.grilla.get((d, 'T'), "")
    
    # Selectbox con default seguro
    new_m = c2.selectbox(f"M {d}", [""] + st.session_state.agentes, 
                         index=([""] + st.session_state.agentes).index(val_m) if val_m in [""] + st.session_state.agentes else 0,
                         key=f"sel_M_{d}")
    new_t = c3.selectbox(f"T {d}", [""] + st.session_state.agentes, 
                         index=([""] + st.session_state.agentes).index(val_t) if val_t in [""] + st.session_state.agentes else 0,
                         key=f"sel_T_{d}")
    
    st.session_state.grilla[(d, 'M')] = new_m
    st.session_state.grilla[(d, 'T')] = new_t

if st.sidebar.button("🗑️ Limpiar"):
    st.session_state.grilla = {}
    st.rerun()
