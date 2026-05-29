import streamlit as st
import pandas as pd
import calendar
from datetime import date

st.set_page_config(layout="wide")

# Inicialización
if 'agentes' not in st.session_state:
    st.session_state.agentes = {
        "Barros": {"pref_m": [], "pref_t": [], "disp_m": [], "disp_t": [], "bloqueos": []},
        "Garcia": {"pref_m": [], "pref_t": [], "disp_m": [], "disp_t": [], "bloqueos": []},
        "Sanchez": {"pref_m": [], "pref_t": [], "disp_m": [], "disp_t": [], "bloqueos": []},
        "Ricartez": {"pref_m": [], "pref_t": [], "disp_m": [], "disp_t": [], "bloqueos": []}
    }

if 'grilla_data' not in st.session_state:
    st.session_state.grilla_data = {}

st.title("🗓️ Planificador - Motor de Asignación")

mes_anio = st.date_input("Seleccionar mes", value=date(2026, 6, 1))
dias_mes = calendar.monthrange(mes_anio.year, mes_anio.month)[1]
lista_dias = list(range(1, dias_mes + 1))
dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]

with st.sidebar:
    for nombre in st.session_state.agentes:
        with st.expander(f"Agente: {nombre}"):
            st.session_state.agentes[nombre]['pref_m'] = st.multiselect("Días exactos (M)", lista_dias, key=f"dm_{nombre}")
            st.session_state.agentes[nombre]['pref_t'] = st.multiselect("Días exactos (T)", lista_dias, key=f"dt_{nombre}")
            st.session_state.agentes[nombre]['disp_m'] = st.multiselect("Semanal (M)", dias_semana, key=f"sm_{nombre}")
            st.session_state.agentes[nombre]['disp_t'] = st.multiselect("Semanal (T)", dias_semana, key=f"st_{nombre}")
            st.session_state.agentes[nombre]['bloqueos'] = st.multiselect("Días NO trabajar", lista_dias, key=f"bl_{nombre}")

    if st.button("🚀 Autocompletar"):
        # Resetear datos de la grilla
        st.session_state.grilla_data = {(d, t): "" for d in lista_dias for t in ['M', 'T']}
        
        for d in lista_dias:
            fecha = date(mes_anio.year, mes_anio.month, d)
            dia_nombre = dias_semana[fecha.weekday()]
            
            for t in ['M', 'T']:
                candidatos = [n for n, cfg in st.session_state.agentes.items() if d not in cfg['bloqueos']]
                if candidatos:
                    # Ordenar: 1) Preferentes, 2) Menos turnos acumulados
                    candidatos.sort(key=lambda n: (
                        0 if (d in (st.session_state.agentes[n]['pref_m'] if t == 'M' else st.session_state.agentes[n]['pref_t']) or 
                              dia_nombre in (st.session_state.agentes[n]['disp_m'] if t == 'M' else st.session_state.agentes[n]['disp_t'])) 
                        else 1,
                        sum(1 for k, v in st.session_state.grilla_data.items() if v == n)
                    ))
                    st.session_state.grilla_data[(d, t)] = candidatos[0]
        st.rerun()

# Mostrar Planilla
for d in lista_dias:
    cols = st.columns([1, 1, 4, 4])
    cols[0].write(f"**{d}**")
    
    # Asignar valores desde el estado
    m_val = st.session_state.grilla_data.get((d, 'M'), "")
    t_val = st.session_state.grilla_data.get((d, 'T'), "")
    
    options = [""] + list(st.session_state.agentes.keys())
    
    st.session_state.grilla_data[(d, 'M')] = cols[2].selectbox(f"M {d}", options, index=options.index(m_val) if m_val in options else 0, key=f"m_{d}")
    st.session_state.grilla_data[(d, 'T')] = cols[3].selectbox(f"T {d}", options, index=options.index(t_val) if t_val in options else 0, key=f"t_{d}")
