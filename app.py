if btn_guardar:
    if nombre:
        try:
            ahora = datetime.now()
            # Crear nueva fila
            nuevo_registro = pd.DataFrame([{
                "asesor": nombre,
                "etapa": etapa,
                "fecha": ahora.strftime("%Y-%m-%d"),
                "mes_texto": ahora.strftime("%B"),
                "semana_año": int(ahora.isocalendar()[1])
            }])
            
            # Combinar datos
            df_actualizado = pd.concat([df, nuevo_registro], ignore_index=True)
            
            # GUARDAR: Usamos el link directo de los secrets para asegurar conexión
            conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_actualizado)
            
            st.sidebar.success(f"✅ ¡Registrado para {nombre}!")
            st.rerun()
        except Exception as e:
            st.error(f"Error al guardar: {e}")
    else:
        st.sidebar.error("⚠️ Por favor ingresa tu nombre.")
