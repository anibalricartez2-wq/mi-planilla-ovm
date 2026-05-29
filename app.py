import streamlit as st
import pandas as pd
import calendar
from datetime import date

st.set_page_config(layout="wide")

# Inicialización
if 'agentes' not in st.session_state:
    st.session_state.agentes = {
        "Barros": {"pref_m": [], "pref_t": [], "bloqueos": []},
        "Garcia": {"pref_m": [], "pref_t": [], "bloqueos": []},
        "Sanchez": {"pref_m": [], "pref_t": [], "bloqueos": []},
        "Ricartez": {"pref_m": [], "pref_t": [], "bloqueos": []}
    }

st.title("🗓️ Planificador de Turnos - Asignación por Día")

mes_anio = st.date_input("Seleccionar mes", value=date(2026, 6, 1))
dias_mes = calendar.monthrange(mes_anio.year, mes_anio.month)[1]
lista_dias = list(range(1, dias_mes + 1))

# --- SIDEBAR: PREFERENCIAS POR DÍA DEL MES ---
with st.sidebar:
    st.header("⚙️ Preferencias (Días del Mes)")
    for nombre in st.session_state.agentes:
        with st.expander(f"Agente: {nombre}"):
            st.session_state.agentes[nombre]['pref_m'] = st.multiselect("Días (M)", lista_dias, key=f"dm_{nombre}")
            st.session_state.agentes[nombre]['pref_t'] = st.multiselect("Días (T)", lista_dias, key=f"dt_{nombre}")
            st.session_state.agentes[nombre]['bloqueos'] = st.multiselect("Días NO trabajar", lista_dias, key=f"bl_{nombre}")

# --- LÓGICA DE AUTOCOMPLETADO ---
def autocompletar():
    # Primero: Asignar según preferencias marcadas
    for d in lista_dias:
        for t in ['M', 'T']:
            if st.session_state.grilla.loc[d, t] == "":
                # Buscar quien marcó preferencia para este día y turno
                for n, cfg in st.session_state.agentes.items():
                    pref = cfg['pref_m'] if t == 'M' else cfg['pref_t']
                    if d in pref and d not in cfg['bloqueos']:
                        st.session_state.grilla.loc[d, t] = n
                        break
    
    # Segundo: Rellenar huecos equitativamente
    for d in lista_dias:
        for t in ['M', 'T']:
            if st.session_state.grilla.loc[d, t] == "":
                candidatos = [n for n in st.session_state.agentes.keys() if d not in st.session_state.agentes[n]['bloqueos']]
                if candidatos:
                    # Ordenar por quien tiene menos turnos totales
                    candidatos.sort(key=lambda n: sum((st.session_state.grilla == n).sum()))
                    st.session_state.grilla.loc[d, t] = candidatos[0]

if 'grilla' not in st.session_state:
    st.session_state.grilla = pd.DataFrame(index=lista_dias, columns=['M', 'T']).fillna("")

if st.sidebar.button("🚀 Autocompletar Planilla"):
    autocompletar()

# Visualización
for d in lista_dias:
    cols = st.columns([1, 1, 4, 4])
    cols[0].write(f"**Día {d}**")
    
    # Selectbox manual para correcciones
    st.session_state.grilla.loc[d, 'M'] = cols[2].selectbox(f"M {d}", [""] + list(st.session_state.agentes.keys()), 
                               key=f"m_{d}", index=0 if st.session_state.grilla.loc[d, 'M'] == "" else list(st.session_state.agentes.keys()).index(st.session_state.grilla.loc[d, 'M']) + 1)
    
    st.session_state.grilla.loc[d, 'T'] = cols[3].selectbox(f"T {d}", [""] + list(st.session_state.agentes.keys()), 
                               key=f"t_{d}", index=0 if st.session_state.grilla.loc[d, 'T'] == "" else list(st.session_state.agentes.keys()).index(st.session_state.grilla.loc[d, 'T']) + 1)
