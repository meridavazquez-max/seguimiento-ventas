import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Seguimiento de Ventas", layout="wide", page_icon="📈")

st.title("🛡️ Sistema de Control de Ventas - Seguros")
st.markdown("Registro rápido para asesores y visualización de metas semanales.")

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # ttl=0 para que siempre lea datos nuevos
        return conn.read(ttl=0).dropna(how="all")
    except:
        return pd.DataFrame(columns=["asesor", "etapa", "fecha", "mes_texto", "semana_año"])

df = cargar_datos()

# --- BARRA LATERAL: REGISTRO DE DATOS ---
with st.sidebar:
    st.header("📝 Registrar Actividad")
    with st.form("form_registro", clear_on_submit=True):
        nombre = st.text_input("Nombre del Asesor").upper().strip()
        etapa = st.selectbox("Etapa del Proceso", 
                             ["Cita Inicial", "Cita de Cierre", "Emisión de Póliza", "Póliza Pagada"])
        
        btn_guardar = st.form_submit_button("Guardar Registro")

if btn_guardar:
    if nombre:
        try:
            ahora = datetime.now()
            nuevo_registro = pd.DataFrame([{
                "asesor": nombre,
                "etapa": etapa,
                "fecha": ahora.strftime("%Y-%m-%d"),
                "mes_texto": ahora.strftime("%B"),
                "semana_año": int(ahora.isocalendar()[1])
            }])
            
            # Combinar datos viejos con el nuevo
            df_actualizado = pd.concat([df, nuevo_registro], ignore_index=True)
            
            # Guardar usando el link de los secrets
            conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_actualizado)
            
            st.sidebar.success(f"✅ ¡Registrado para {nombre}!")
            st.rerun()
        except Exception as e:
            st.error(f"Error al guardar: {e}. Revisa que tu Google Sheet tenga permisos de EDITOR.")
    else:
        st.sidebar.error("⚠️ Por favor ingresa tu nombre.")

# --- DASHBOARD PRINCIPAL ---
if not df.empty:
    # Métricas simples
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Movimientos", len(df))
    m2.metric("Pólizas Pagadas", len(df[df['etapa'] == "Póliza Pagada"]))
    m3.metric("Asesores Activos", df['asesor'].nunique())

    st.divider()

    st.subheader("📈 Rendimiento por Asesor")
    # Tabla resumen por etapas
    resumen = df.groupby(['asesor', 'etapa']).size().unstack(fill_value=0)
    st.dataframe(resumen, use_container_width=True)

    with st.expander("Ver historial completo"):
        st.write(df.sort_values(by='fecha', ascending=False))
else:
    st.info("👋 ¡Bienvenido! Ingresa el primer registro en el panel de la izquierda para comenzar.")
