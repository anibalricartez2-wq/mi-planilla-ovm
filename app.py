import streamlit as st
import pandas as pd
import calendar
from datetime import date

st.set_page_config(layout="wide")

# 1. Inicialización de datos
if 'agentes' not in st.session_state:
    st.session_state.agentes = {
        "Barros": {"pref_m": [], "pref_t": [], "bloqueos": []},
        "Garcia": {"pref_m": [], "pref_t": [], "bloqueos": []},
        "Sanchez": {"pref_m": [], "pref_t": [], "bloqueos": []},
        "Ricartez": {"pref_m": [], "pref_t": [], "bloqueos": []}
    }

st.title("🗓️ Planificador con Control de Equidad")

# 2. Selección del mes
mes_anio = st.date_input("Seleccionar mes", value=date(2026, 6, 1))
dias_mes = calendar.monthrange(mes_anio.year, mes_anio.month)[1]
lista_dias = list(range(1, dias_mes + 1))

# 3. Inicialización/Reinicio de Grilla si cambia el mes
if 'mes_actual' not in st.session_state or st.session_state.mes_actual != mes_anio.month:
    st.session_state.grilla = pd.DataFrame(index=lista_dias, columns=['M', 'T']).fillna("")
    st.session_state.mes_actual = mes_anio.month

# 4. Sidebar para preferencias
with st.sidebar:
    st.header("⚙️ Preferencias y Bloqueos")
    for nombre in st.session_state.agentes:
        with st.expander(f"Agente: {nombre}"):
            st.session_state.agentes[nombre]['pref_m'] = st.multiselect("Prefiere Mañana", lista_dias, key=f"m_{nombre}")
            st.session_state.agentes[nombre]['pref_t'] = st.multiselect("Prefiere Tarde", lista_dias, key=f"t_{nombre}")
            st.session_state.agentes[nombre]['bloqueos'] = st.multiselect("Días NO trabajar", lista_dias, key=f"b_{nombre}")

# 5. Visualización de Casillas
st.subheader("Asignación de Turnos")
for d in lista_dias:
    cols = st.columns([1, 1, 4, 4])
    cols[0].write(f"**Día {d}**")
    
    # Usamos un callback para actualizar el estado del dataframe sin errores de loc
    val_m = cols[2].selectbox(f"Mañana {d}", [""] + list(st.session_state.agentes.keys()), 
                              index=0 if st.session_state.grilla.loc[d, 'M'] == "" else list(st.session_state.agentes.keys()).index(st.session_state.grilla.loc[d, 'M']) + 1,
                              key=f"m_sel_{d}")
    
    val_t = cols[3].selectbox(f"Tarde {d}", [""] + list(st.session_state.agentes.keys()), 
                              index=0 if st.session_state.grilla.loc[d, 'T'] == "" else list(st.session_state.agentes.keys()).index(st.session_state.grilla.loc[d, 'T']) + 1,
                              key=f"t_sel_{d}")
    
    st.session_state.grilla.loc[d, 'M'] = val_m
    st.session_state.grilla.loc[d, 'T'] = val_t

# 6. Botón de Validación
if st.button("📊 Validar Equidad y Cargas"):
    st.subheader("📊 Análisis de Equidad (M vs T)")
    data_resumen = []
    
    for nombre in st.session_state.agentes:
        puntos = 0
        turnos_m = 0
        turnos_t = 0
        for d in lista_dias:
            fecha_actual = date(mes_anio.year, mes_anio.month, d)
            valor_dia = 18 if fecha_actual.weekday() >= 5 else 9
            if st.session_state.grilla.loc[d, 'M'] == nombre:
                turnos_m += 1
                puntos += valor_dia
            if st.session_state.grilla.loc[d, 'T'] == nombre:
                turnos_t += 1
                puntos += valor_dia
        data_resumen.append({"Agente": nombre, "Turnos M": turnos_m, "Turnos T": turnos_t, "Puntos Totales": puntos})
    
    df_resumen = pd.DataFrame(data_resumen)
    st.table(df_resumen)
