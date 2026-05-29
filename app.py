import streamlit as st
import pandas as pd
import calendar
from datetime import date

st.set_page_config(layout="wide")

if 'agentes' not in st.session_state:
    st.session_state.agentes = {
        "Barros": {"pref_m": [], "pref_t": [], "bloqueos": []},
        "Garcia": {"pref_m": [], "pref_t": [], "bloqueos": []},
        "Sanchez": {"pref_m": [], "pref_t": [], "bloqueos": []},
        "Ricartez": {"pref_m": [], "pref_t": [], "bloqueos": []}
    }

st.title("🗓️ Planificador con Control de Equidad")

mes_anio = st.date_input("Seleccionar mes", value=date(2026, 6, 1))
dias_mes = calendar.monthrange(mes_anio.year, mes_anio.month)[1]
lista_dias = list(range(1, dias_mes + 1))

# Sidebar para preferencias
with st.sidebar:
    st.header("⚙️ Preferencias y Bloqueos")
    for nombre in st.session_state.agentes:
        with st.expander(f"Agente: {nombre}"):
            st.session_state.agentes[nombre]['pref_m'] = st.multiselect("Prefiere Mañana", lista_dias, key=f"m_{nombre}")
            st.session_state.agentes[nombre]['pref_t'] = st.multiselect("Prefiere Tarde", lista_dias, key=f"t_{nombre}")
            st.session_state.agentes[nombre]['bloqueos'] = st.multiselect("Días NO trabajar", lista_dias, key=f"b_{nombre}")

# Grilla de asignación
if 'grilla' not in st.session_state:
    st.session_state.grilla = pd.DataFrame(index=lista_dias, columns=['M', 'T'])

for d in lista_dias:
    cols = st.columns([1, 1, 4, 4])
    cols[0].write(f"**Día {d}**")
    st.session_state.grilla.loc[d, 'M'] = cols[2].selectbox(f"Mañana {d}", [""] + list(st.session_state.agentes.keys()), key=f"m_sel_{d}")
    st.session_state.grilla.loc[d, 'T'] = cols[3].selectbox(f"Tarde {d}", [""] + list(st.session_state.agentes.keys()), key=f"t_sel_{d}")

if st.button("📊 Validar Equidad y Cargas"):
    st.subheader("📊 Análisis de Equidad (M vs T)")
    
    # Tabla para mostrar conteos
    data_resumen = []
    
    for nombre in st.session_state.agentes:
        puntos = 0
        turnos_m = 0
        turnos_t = 0
        
        for d in lista_dias:
            fecha_actual = date(mes_anio.year, mes_anio.month, d)
            valor_dia = 18 if fecha_actual.weekday() >= 5 else 9
            
            # Sumar M
            if st.session_state.grilla.loc[d, 'M'] == nombre:
                turnos_m += 1
                puntos += valor_dia
            # Sumar T
            if st.session_state.grilla.loc[d, 'T'] == nombre:
                turnos_t += 1
                puntos += valor_dia
                
        data_resumen.append({"Agente": nombre, "Turnos M": turnos_m, "Turnos T": turnos_t, "Puntos Totales": puntos})
    
    df_resumen = pd.DataFrame(data_resumen)
    st.table(df_resumen)
    
    # Alerta si hay desigualdad
    st.subheader("⚠️ Avisos de Desigualdad")
    max_m = df_resumen['Turnos M'].max()
    min_m = df_resumen['Turnos M'].min()
    if max_m - min_m > 1:
        st.warning(f"Desigualdad en Mañanas: La diferencia entre el que más y menos tiene es de {max_m - min_m} turnos.")
    else:
        st.success("Distribución de mañanas equitativa.")
