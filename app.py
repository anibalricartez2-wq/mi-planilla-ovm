def autocompletar():
    # Iterar por cada celda de la planilla
    for d in lista_dias:
        fecha = date(mes_anio.year, mes_anio.month, d)
        dia_nombre = dias_semana[fecha.weekday()]
        
        for t in ['M', 'T']:
            if st.session_state.grilla.loc[d, t] == "":
                
                # 1. Buscar candidatos que marcaron preferencia Específica o Semanal
                # (Excluyendo bloqueados)
                candidatos_preferentes = [
                    n for n, cfg in st.session_state.agentes.items()
                    if d not in cfg['bloqueos'] and 
                    (d in (cfg['pref_m'] if t == 'M' else cfg['pref_t']) or 
                     dia_nombre in (cfg['disp_m'] if t == 'M' else cfg['disp_t']))
                ]
                
                # 2. Si no hay preferentes, usar TODOS los que no están bloqueados (Comodines)
                candidatos_comodines = [
                    n for n, cfg in st.session_state.agentes.items()
                    if d not in cfg['bloqueos']
                ]
                
                # Elegir lista (Priorizar preferentes si existen, sino usar comodines)
                lista_final = candidatos_preferentes if candidatos_preferentes else candidatos_comodines
                
                # 3. Asignar al que menos turnos tiene en total (Equidad)
                if lista_final:
                    lista_final.sort(key=lambda n: sum((st.session_state.grilla == n).sum()))
                    st.session_state.grilla.loc[d, t] = lista_final[0]
