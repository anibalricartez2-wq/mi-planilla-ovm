import streamlit as st
import pandas as pd
import calendar

st.set_page_config(layout="wide")

# Inicialización de estado para persistir los datos
if 'grilla' not in st.session_state:
    st.session_state.grilla = {} # Aquí guardaremos {fecha: {'M': '...', 'T': '...'}}
    st.session_state.agentes = {
        "Barros": {"pref_m": [], "pref_t": [], "bloqueos": [], "licencias": [], "puntos": 0},
        "Garcia": {"pref_m": [], "pref_t": [], "bloqueos": [], "licencias": [], "puntos": 0},
        "Sanchez": {"pref_m": [], "pref_t": [], "bloqueos": [], "licencias": [], "puntos": 0},
        "Ricartez": {"pref_m": [], "pref_t": [], "bloqueos": [], "licencias": [], "puntos": 0}
    }

st.title("🗓️ Planificador de Turnos - Asistente de Gestión")

# 1. Configuración del Mes
mes_anio = st.date_input("Seleccionar mes", value=pd.to_datetime("2026-06-01"))
meta_horas = st.number_input("Meta de puntos mensuales por agente", value=130)

# 2. Sidebar: Gestión de Agentes
with st.sidebar:
    st.header("⚙️ Configuración de Agentes")
    for nombre in st.session_state.agentes:
        with st.expander(f"Agente: {nombre}"):
            st.session_state.agentes[nombre]['pref_m'] = st.multiselect("Preferencia Mañana", ["Lu","Ma","Mi","Ju","Vi","Sá","Do"], key=f"m_{nombre}")
            st.session_state.agentes[nombre]['pref_t'] = st.multiselect("Preferencia Tarde", ["Lu","Ma","Mi","Ju","Vi","Sá","Do"], key=f"t_{nombre}")
            st.session_state.agentes[nombre]['bloqueos'] = st.text_input("Días bloqueados (ej: 1, 5, 20)", key=f"b_{nombre}")

# 3. Visualización de Casillas (Matriz)
st.subheader("Asignación de Turnos")
dias_mes = calendar.monthrange(mes_anio.year, mes_anio.month)[1]

# Crear dataframe de trabajo
cols = st.columns([1, 1, 2, 2])
for d in range(1, dias_mes + 1):
    fecha = f"{mes_anio.year}-{mes_anio.month:02d}-{d:02d}"
    dia_sem = calendar.day_abbr[calendar.weekday(mes_anio.year, mes_anio.month, d)]
    
    with st.container():
        c1, c2, c3, c4 = st.columns([1, 1, 2, 2])
        c1.write(f"**{d}**")
        c2.write(f"{dia_sem}")
        
        # Selección de turnos
        asignacion_m = c3.selectbox(f"Mañana {d}", [""] + list(st.session_state.agentes.keys()), key=f"m_{d}")
        asignacion_t = c4.selectbox(f"Tarde {d}", [""] + list(st.session_state.agentes.keys()), key=f"t_{d}")

# 4. Cálculo de Estado
if st.button("Calcular Estado Actual"):
    # Aquí irá la lógica que suma los puntos (9 o 18) y compara con la meta
    st.write("---")
    st.subheader("Estado de Cumplimiento")
    for nombre, datos in st.session_state.agentes.items():
        st.write(f"**{nombre}**: {datos['puntos']} puntos acumulados. Faltan: {max(0, meta_horas - datos['puntos'])} puntos.")
