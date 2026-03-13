import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control de Ventas", layout="wide")

st.title("📈 Sistema de Seguimiento de Ventas")
st.markdown("Herramienta para el registro de citas y emisiones.")

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Intentar leer datos
try:
    df = conn.read(ttl=0)
    df = df.dropna(how="all")
except Exception as e:
    st.error("No se pudo leer la base de datos. Verifica el link en Secrets.")
    df = pd.DataFrame(columns=["asesor", "etapa", "fecha", "mes_texto", "semana_año"])

# --- FORMULARIO ---
with st.sidebar:
    st.header("📝 Nuevo Registro")
    with st.form("registro_ventas", clear_on_submit=True):
        nombre = st.text_input("Nombre del Asesor").upper().strip()
        etapa = st.selectbox("Etapa", ["Cita Inicial", "Cita de Cierre", "Emisión de Póliza", "Póliza Pagada"])
        submit = st.form_submit_button("Guardar Registro")

if submit:
    if nombre:
        ahora = datetime.now()
        nuevo_dato = {
            "asesor": nombre,
            "etapa": etapa,
            "fecha": ahora.strftime("%Y-%m-%d"),
            "mes_texto": ahora.strftime("%B"),
            "semana_año": int(ahora.isocalendar()[1])
        }
        
        # Crear el nuevo DataFrame
        nuevo_df = pd.DataFrame([nuevo_dato])
        df_final = pd.concat([df, nuevo_df], ignore_index=True)
        
        try:
            # Intentar actualizar la hoja
            conn.update(data=df_final)
            st.sidebar.success(f"✅ ¡Registrado para {nombre}!")
            st.rerun()
        except Exception as e:
            st.error("⚠️ Google bloqueó el guardado directo.")
            st.info("Para solucionar esto, asegúrate de que el link en 'Secrets' termine en '/edit' y que compartieras la hoja como EDITOR.")
    else:
        st.sidebar.warning("Escribe un nombre.")

# --- VISUALIZACIÓN ---
if not df.empty:
    st.subheader("Resumen de Rendimiento")
    # Tabla pivote para ver citas y ventas por asesor
    resumen = df.groupby(['asesor', 'etapa']).size().unstack(fill_value=0)
    st.dataframe(resumen, use_container_width=True)
    
    with st.expander("Ver Historial Completo"):
        st.write(df.sort_values(by="fecha", ascending=False))
else:
    st.info("Esperando el primer registro...")
