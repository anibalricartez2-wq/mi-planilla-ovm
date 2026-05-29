import streamlit as st
import pandas as pd
import calendar
from datetime import date

st.set_page_config(layout="wide")

# Inicialización
if 'agentes' not in st.session_state:
    st.session_state.agentes = {
        "Barros": {"disp_m": [], "disp_t": [], "bloqueos": []},
        "Garcia": {"disp_m": [], "disp_t": [], "bloqueos": []},
        "Sanchez": {"disp_m": [], "disp_t": [], "bloqueos": []},
        "Ricartez": {"disp_m": [], "disp_t": [], "bloqueos": []}
    }

st.title("🗓️ Planificador con Restricciones Semanales")

mes_anio = st.date_input("Seleccionar mes", value=date(2026, 6, 1))
dias_mes = calendar.monthrange(mes_anio.year, mes_anio.month)[1]
lista_dias = list(range(1, dias_mes + 1))
dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]

# --- SIDEBAR: CONFIGURACIÓN POR AGENTE ---
with st.sidebar:
    st.header("⚙️ Configuración")
    for nombre in st.session_state.agentes:
        with st.expander(f"Agente: {nombre}"):
            st.session_state.agentes[nombre]['disp_m'] = st.multiselect("Días semana Mañana", dias_semana, key=f"dm_{nombre}")
            st.session_state.agentes[nombre]['disp_t'] = st.multiselect("Días semana Tarde", dias_semana, key=f"dt_{nombre}")
            st.session_state.agentes[nombre]['bloqueos'] = st.multiselect("Días NO trabajar", lista_dias, key=f"bl_{nombre}")

# --- MOTOR DE AUTOCOMPLETADO ---
def autocompletar():
    for d in lista_dias:
        fecha = date(mes_anio.year, mes_anio.month, d)
        dia_nombre = dias_semana[fecha.weekday()]
        
        for t in ['M', 'T']:
            if st.session_state.grilla.loc[d, t] == "":
                # Filtrar candidatos que: 1. No estén bloqueados, 2. Tengan disponibilidad ese día
                candidatos = [n for n, cfg in st.session_state.agentes.items() 
                              if d not in cfg['bloqueos'] and 
                              (dia_nombre in (cfg['disp_m'] if t == 'M' else cfg['disp_t']))]
                
                if candidatos:
                    # Ordenar por el que menos turnos tenga (Equidad)
                    candidatos.sort(key=lambda n: sum((st.session_state.grilla == n).sum()))
                    st.session_state.grilla.loc[d, t] = candidatos[0]

# --- INTERFAZ ---
if 'grilla' not in st.session_state:
    st.session_state.grilla = pd.DataFrame(index=lista_dias, columns=['M', 'T']).fillna("")

if st.sidebar.button("🚀 Autocompletar Planilla"):
    autocompletar()

for d in lista_dias:
    cols = st.columns([1, 1, 4, 4])
    cols[0].write(f"**{d}** ({dias_semana[date(mes_anio.year, mes_anio.month, d).weekday()]})")
    st.session_state.grilla.loc[d, 'M'] = cols[2].selectbox(f"M {d}", [""] + list(st.session_state.agentes.keys()), key=f"m_{d}")
    st.session_state.grilla.loc[d, 'T'] = cols[3].selectbox(f"T {d}", [""] + list(st.session_state.agentes.keys()), key=f"t_{d}")
