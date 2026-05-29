import streamlit as st
import pandas as pd
import calendar
from datetime import date

st.set_page_config(layout="wide")

# Inicialización del estado
if 'agentes' not in st.session_state:
    st.session_state.agentes = {
        "Barros": {"pref_m": [], "pref_t": [], "disp_m": [], "disp_t": [], "bloqueos": []},
        "Garcia": {"pref_m": [], "pref_t": [], "disp_m": [], "disp_t": [], "bloqueos": []},
        "Sanchez": {"pref_m": [], "pref_t": [], "disp_m": [], "disp_t": [], "bloqueos": []},
        "Ricartez": {"pref_m": [], "pref_t": [], "disp_m": [], "disp_t": [], "bloqueos": []}
    }

st.title("🗓️ Planificador de Turnos - Autocompletado Equitativo")

mes_anio = st.date_input("Seleccionar mes", value=date(2026, 6, 1))
dias_mes = calendar.monthrange(mes_anio.year, mes_anio.month)[1]
lista_dias = list(range(1, dias_mes + 1))
dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]

# Inicializar grilla si no existe o cambió el mes
if 'grilla' not in st.session_state or st.session_state.get('mes_actual') != mes_anio.month:
    st.session_state.grilla = pd.DataFrame(index=lista_dias, columns=['M', 'T']).fillna("")
    st.session_state.mes_actual = mes_anio.month

# --- SIDEBAR: CONFIGURACIÓN ---
with st.sidebar:
    st.header("⚙️ Configuración")
    for nombre in st.session_state.agentes:
        with st.expander(f"Agente: {nombre}"):
            st.write("--- Días del Mes ---")
            st.session_state.agentes[nombre]['pref_m'] = st.multiselect("Días exactos (M)", lista_dias, key=f"dm_{nombre}")
            st.session_state.agentes[nombre]['pref_t'] = st.multiselect("Días exactos (T)", lista_dias, key=f"dt_{nombre}")
            st.write("--- Días de la Semana ---")
            st.session_state.agentes[nombre]['disp_m'] = st.multiselect("Semanal (M)", dias_semana, key=f"sm_{nombre}")
            st.session_state.agentes[nombre]['disp_t'] = st.multiselect("Semanal (T)", dias_semana, key=f"st_{nombre}")
            st.write("--- Bloqueos ---")
            st.session_state.agentes[nombre]['bloqueos'] = st.multiselect("Días NO trabajar", lista_dias, key=f"bl_{nombre}")

# --- MOTOR DE AUTOCOMPLETADO ---
def autocompletar():
    for d in lista_dias:
        fecha = date(mes_anio.year, mes_anio.month, d)
        dia_nombre = dias_semana[fecha.weekday()]
        
        for t in ['M', 'T']:
            if st.session_state.grilla.loc[d, t] == "":
                # 1. Candidatos preferentes (Día exacto o Semanal)
                candidatos_preferentes = [
                    n for n, cfg in st.session_state.agentes.items()
                    if d not in cfg['bloqueos'] and 
                    (d in (cfg['pref_m'] if t == 'M' else cfg['pref_t']) or 
                     dia_nombre in (cfg['disp_m'] if t == 'M' else cfg['disp_t']))
                ]
                
                # 2. Comodines (Cualquiera que no esté bloqueado)
                candidatos_comodines = [
                    n for n, cfg in st.session_state.agentes.items()
                    if d not in cfg['bloqueos']
                ]
                
                # Priorizar preferentes, sino usar comodines
                lista_final = candidatos_preferentes if candidatos_preferentes else candidatos_comodines
                
                if lista_final:
                    # Ordenar por el que menos turnos tiene en total (Equidad)
                    lista_final.sort(key=lambda n: sum((st.session_state.grilla == n).sum()))
                    st.session_state.grilla.loc[d, t] = lista_final[0]

if st.sidebar.button("🚀 Autocompletar Planilla"):
    autocompletar()

# Visualización y edición manual
for d in lista_dias:
    cols = st.columns([1, 1, 4, 4])
    cols[0].write(f"**{d}** ({dias_semana[date(mes_anio.year, mes_anio.month, d).weekday()]})")
    
    val_m = cols[2].selectbox(f"M {d}", [""] + list(st.session_state.agentes.keys()), 
                               key=f"m_{d}", index=0 if st.session_state.grilla.loc[d, 'M'] == "" else list(st.session_state.agentes.keys()).index(st.session_state.grilla.loc[d, 'M']) + 1)
    val_t = cols[3].selectbox(f"T {d}", [""] + list(st.session_state.agentes.keys()), 
                               key=f"t_{d}", index=0 if st.session_state.grilla.loc[d, 'T'] == "" else list(st.session_state.agentes.keys()).index(st.session_state.grilla.loc[d, 'T']) + 1)
    
    st.session_state.grilla.loc[d, 'M'] = val_m
    st.session_state.grilla.loc[d, 'T'] = val_t
