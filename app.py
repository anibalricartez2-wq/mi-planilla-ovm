import streamlit as st

# Configuración básica
st.set_page_config(layout="wide")

# 1. ESTADO INICIAL
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {} # Almacena: (dia, turno): nombre

st.title("🗓️ Planificador de Turnos - Gestión Equitativa")

# 2. CONFIGURACIÓN SIDEBAR
with st.sidebar:
    st.header("Configuración de Agentes")
    for n in st.session_state.agentes:
        with st.expander(f"Agente: {n}"):
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Días exactos (Mañana)", range(1, 32), key=f"dm_{n}")
            st.session_state.prefs[n]['bloq'] = st.multiselect("Días NO trabajar", range(1, 32), key=f"bl_{n}")

# 3. MOTOR DE AUTOCOMPLETADO
def autocompletar():
    # Limpiamos solo si queremos borrar todo, o mantenemos lo existente
    # Para forzar el llenado, limpiamos la grilla
    st.session_state.grilla = {}
    
    dias = range(1, 32)
    for d in dias:
        for t in ['M', 'T']:
            # Elegir candidatos válidos (los que NO están bloqueados ese día)
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            
            # Orden: 
            # 1. Preferencia (si tiene preferencia en este día/turno -> prioridad)
            # 2. Equidad (el que menos turnos tenga acumulados en la grilla)
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
st.write("---")
for d in range(1, 32):
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"### Día {d}")
    
    # Valores actuales
    val_m = st.session_state.grilla.get((d, 'M'), "")
    val_t = st.session_state.grilla.get((d, 'T'), "")
    
    # Selectores
    new_m = c2.selectbox(f"Mañana {d}", [""] + st.session_state.agentes, 
                         index=([""] + st.session_state.agentes).index(val_m) if val_m in [""] + st.session_state.agentes else 0,
                         key=f"M_{d}")
    new_t = c3.selectbox(f"Tarde {d}", [""] + st.session_state.agentes, 
                         index=([""] + st.session_state.agentes).index(val_t) if val_t in [""] + st.session_state.agentes else 0,
                         key=f"T_{d}")
    
    # Guardar cambios
    st.session_state.grilla[(d, 'M')] = new_m
    st.session_state.grilla[(d, 'T')] = new_t

# Botón para limpiar
if st.sidebar.button("🗑️ Limpiar Planilla"):
    st.session_state.grilla = {}
    st.rerun()
