import streamlit as st

st.set_page_config(layout="wide")

# 1. ESTADO INICIAL
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "disp_m":[], "disp_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {} 

st.title("🗓️ Planificador - Motor de Asignación")

# 2. MENU DE RESTRICCIONES AMPLIADO
with st.sidebar:
    st.header("Configuración de Restricciones")
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.write("**Días del mes (exactos)**")
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Mañana", range(1, 32), key=f"dm_{n}")
            st.session_state.prefs[n]['pref_t'] = st.multiselect("Tarde", range(1, 32), key=f"dt_{n}")
            st.write("**Disponibilidad semanal (Lu-Do)**")
            st.session_state.prefs[n]['disp_m'] = st.multiselect("Semanal Mañana", ["Lu","Ma","Mi","Ju","Vi","Sá","Do"], key=f"sm_{n}")
            st.session_state.prefs[n]['disp_t'] = st.multiselect("Semanal Tarde", ["Lu","Ma","Mi","Ju","Vi","Sá","Do"], key=f"st_{n}")
            st.session_state.prefs[n]['bloq'] = st.multiselect("Días NO trabajar", range(1, 32), key=f"bl_{n}")

# 3. MOTOR DE AUTOCOMPLETADO
def autocompletar():
    # Creamos un calendario para mapear nombres de día
    dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
    # Limpiamos la grilla para empezar de cero
    st.session_state.grilla = {}
    
    for d in range(1, 32):
        # Calcular día de la semana (asumimos año 2026, mes 6 como base)
        dia_idx = (d - 1) % 7 
        dia_nombre = dias_semana[dia_idx]
        
        for t in ['M', 'T']:
            # Lógica: Candidatos aptos (No bloqueados)
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            
            # Orden: 1. Pref Día, 2. Pref Semanal, 3. Equidad (menos turnos)
            def criterio(n):
                pref_dia = 0 if d in (st.session_state.prefs[n]['pref_m'] if t == 'M' else st.session_state.prefs[n]['pref_t']) else 1
                pref_sem = 0 if dia_nombre in (st.session_state.prefs[n]['disp_m'] if t == 'M' else st.session_state.prefs[n]['disp_t']) else 1
                turnos = sum(1 for k, v in st.session_state.grilla.items() if v == n)
                return (pref_dia, pref_sem, turnos)
            
            cands.sort(key=criterio)
            if cands:
                st.session_state.grilla[(d, t)] = cands[0]

if st.sidebar.button("🚀 Autocompletar"):
    autocompletar()
    st.rerun()

# 4. INTERFAZ: Usamos 'value' en lugar de 'index' calculado para evitar conflictos
st.write("---")
for d in range(1, 32):
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d}**")
    
    # Obtenemos valor guardado o vacío
    m_actual = st.session_state.grilla.get((d, 'M'), "")
    t_actual = st.session_state.grilla.get((d, 'T'), "")
    
    # Los selectbox actualizan el estado directamente
    st.session_state.grilla[(d, 'M')] = c2.selectbox(f"M {d}", [""] + st.session_state.agentes, 
                                                    key=f"M_{d}", index=0 if m_actual == "" else st.session_state.agentes.index(m_actual) + 1)
    st.session_state.grilla[(d, 'T')] = c3.selectbox(f"T {d}", [""] + st.session_state.agentes, 
                                                    key=f"T_{d}", index=0 if t_actual == "" else st.session_state.agentes.index(t_actual) + 1)
