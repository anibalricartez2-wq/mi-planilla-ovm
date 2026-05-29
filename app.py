import streamlit as st
import calendar
from datetime import date

st.set_page_config(layout="wide")

# 1. ESTADO INICIAL
if 'agentes' not in st.session_state:
    st.session_state.agentes = ["Barros", "Garcia", "Sanchez", "Ricartez"]
    st.session_state.prefs = {n: {"pref_m":[], "pref_t":[], "disp_m":[], "disp_t":[], "bloq":[]} for n in st.session_state.agentes}
    st.session_state.grilla = {}

st.title("🗓️ Planificador de Turnos")

# Selección de mes
fecha_seleccionada = st.date_input("Seleccionar mes", date(2026, 6, 1))
anio, mes = fecha_seleccionada.year, fecha_seleccionada.month
_, num_dias = calendar.monthrange(anio, mes)

# 2. MENU SIDEBAR
with st.sidebar:
    st.header("Restricciones")
    for n in st.session_state.agentes:
        with st.expander(f"Restricciones: {n}"):
            st.session_state.prefs[n]['pref_m'] = st.multiselect("Mañana (Día)", range(1, num_dias+1), key=f"dm_{n}")
            st.session_state.prefs[n]['pref_t'] = st.multiselect("Tarde (Día)", range(1, num_dias+1), key=f"dt_{n}")
            st.session_state.prefs[n]['disp_m'] = st.multiselect("Semanal Mañana", ["Lu","Ma","Mi","Ju","Vi","Sá","Do"], key=f"sm_{n}")
            st.session_state.prefs[n]['disp_t'] = st.multiselect("Semanal Tarde", ["Lu","Ma","Mi","Ju","Vi","Sá","Do"], key=f"st_{n}")
            st.session_state.prefs[n]['bloq'] = st.multiselect("NO trabajar", range(1, num_dias+1), key=f"bl_{n}")

# 3. MOTOR DE AUTOCOMPLETADO
if st.sidebar.button("🚀 Autocompletar"):
    dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
    st.session_state.grilla = {} # Limpiamos la grilla
    
    for d in range(1, num_dias + 1):
        dia_nombre = dias_semana[date(anio, mes, d).weekday()]
        for t in ['M', 'T']:
            cands = [n for n in st.session_state.agentes if d not in st.session_state.prefs[n]['bloq']]
            cands.sort(key=lambda n: (
                0 if d in (st.session_state.prefs[n]['pref_m'] if t == 'M' else st.session_state.prefs[n]['pref_t']) else 1,
                0 if dia_nombre in (st.session_state.prefs[n]['disp_m'] if t == 'M' else st.session_state.prefs[n]['disp_t']) else 1,
                sum(1 for k, v in st.session_state.grilla.items() if v == n)
            ))
            if cands:
                st.session_state.grilla[(d, t)] = cands[0]
    
    # FORZAMOS LA RECARGA COMPLETAMENTE
    st.rerun()

# 4. PLANILLA
st.write("---")
dias_semana_nombres = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]

for d in range(1, num_dias + 1):
    dia_str = dias_semana_nombres[date(anio, mes, d).weekday()]
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d} ({dia_str})**")
    
    # Obtenemos valor del estado
    val_m = st.session_state.grilla.get((d, 'M'), "")
    val_t = st.session_state.grilla.get((d, 'T'), "")
    
    # IMPORTANTE: Usamos un key único que cambie si el autocompletado llena algo
    # Esto obliga a Streamlit a redibujar el selector
    opciones = [""] + st.session_state.agentes
    
    st.session_state.grilla[(d, 'M')] = c2.selectbox(f"M {d}", opciones, 
                                                    index=opciones.index(val_m) if val_m in opciones else 0, 
                                                    key=f"M_{d}_{val_m}")
    st.session_state.grilla[(d, 'T')] = c3.selectbox(f"T {d}", opciones, 
                                                    index=opciones.index(val_t) if val_t in opciones else 0, 
                                                    key=f"T_{d}_{val_t}")

if st.sidebar.button("🗑️ Limpiar"):
    st.session_state.grilla = {}
    st.rerun()
