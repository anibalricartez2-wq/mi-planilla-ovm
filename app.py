import streamlit as st
import calendar
from datetime import date

st.set_page_config(layout="wide")

# 1. ESTADO
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

# 3. MOTOR (Simplificado para evitar conflictos)
def autocompletar():
    dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
    st.session_state.grilla = {}
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

if st.sidebar.button("🚀 Autocompletar"):
    autocompletar()
    st.rerun()

# 4. PLANILLA
st.write("---")
dias_semana_nombres = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]

for d in range(1, num_dias + 1):
    dia_str = dias_semana_nombres[date(anio, mes, d).weekday()]
    c1, c2, c3 = st.columns([1, 2, 2])
    c1.write(f"**Día {d} ({dia_str})**")
    
    # Usamos un valor temporal para el selectbox
    key_m = f"M_{d}_{anio}_{mes}"
    key_t = f"T_{d}_{anio}_{mes}"
    
    val_m = c2.selectbox(f"M {d}", [""] + st.session_state.agentes, key=key_m, index=0 if st.session_state.grilla.get((d, 'M'), "")=="" else [""] + st.session_state.agentes.index(st.session_state.grilla.get((d, 'M'), "")) + 1)
    val_t = c3.selectbox(f"T {d}", [""] + st.session_state.agentes, key=key_t, index=0 if st.session_state.grilla.get((d, 'T'), "")=="" else [""] + st.session_state.agentes.index(st.session_state.grilla.get((d, 'T'), "")) + 1)
    
    st.session_state.grilla[(d, 'M')] = val_m
    st.session_state.grilla[(d, 'T')] = val_t

if st.sidebar.button("🗑️ Limpiar"):
    st.session_state.grilla = {}
    st.rerun()
