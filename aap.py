import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Seguimiento de Ventas", layout="wide", page_icon="📈")

st.title("🛡️ Sistema de Control de Ventas - Seguros")
st.markdown("Registro rápido para asesores y visualización de metas semanales.")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Configura tu URL en los Secrets de Streamlit Cloud: [connections.gsheets] spreadsheet = "URL"
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # ttl=0 asegura que los datos se refresquen en cada carga
    return conn.read(ttl=0).dropna(how="all")

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
        ahora = datetime.now()
        # Crear nueva fila
        nuevo_registro = pd.DataFrame([{
            "asesor": nombre,
            "etapa": etapa,
            "fecha": ahora.strftime("%Y-%m-%d"),
            "mes_texto": ahora.strftime("%B"),
            "semana_año": int(ahora.isocalendar()[1])
        }])
        
        # Concatenar y subir
        df_actualizado = pd.concat([df, nuevo_registro], ignore_index=True)
        conn.update(data=df_actualizado)
        
        st.sidebar.success(f"✅ ¡Registrado para {nombre}!")
        st.rerun()
    else:
        st.sidebar.error("⚠️ Por favor ingresa tu nombre.")

# --- DASHBOARD PRINCIPAL ---
if not df.empty:
    # Lógica de fechas
    df['fecha'] = pd.to_datetime(df['fecha'])
    semana_actual = datetime.now().isocalendar()[1]
    semana_anterior = semana_actual - 1

    # 1. MÉTRICAS CLAVE
    m1, m2, m3, m4 = st.columns(4)
    
    total_hoy = len(df[df['fecha'].dt.date == datetime.now().date()])
    actividad_semana = len(df[df['semana_año'] == semana_actual])
    actividad_prev = len(df[df['semana_año'] == semana_anterior])
    crecimiento = actividad_semana - actividad_prev

    m1.metric("Actividad Hoy", total_hoy)
    m2.metric("Esta Semana", actividad_semana, delta=int(crecimiento))
    m3.metric("Pólizas Pagadas", len(df[df['etapa'] == "Póliza Pagada"]))
    m4.metric("Asesores Activos", df['asesor'].nunique())

    st.divider()

    # 2. GRÁFICO COMPARATIVO SEMANAL
    st.subheader("📊 Comparativa: Esta Semana vs. Anterior")
    df_comp = df[df['semana_año'].isin([semana_actual, semana_anterior])]
    
    if not df_comp.empty:
        # Preparar datos para el gráfico de barras
        pivot_semanal = df_comp.groupby(['semana_año', 'etapa']).size().unstack(fill_value=0)
        # Cambiar números de semana por etiquetas
        pivot_semanal.index = pivot_semanal.index.map({semana_actual: "Semana Actual", semana_anterior: "Semana Anterior"})
        st.bar_chart(pivot_semanal)

    # 3. TABLA DE RENDIMIENTO POR ASESOR
    st.subheader("🏆 Ranking de Rendimiento")
    tabla_asesores = df.groupby(['asesor', 'etapa']).size().unstack(fill_value=0)
    # Asegurar que todas las columnas existan para evitar errores visuales
    for col in ["Cita Inicial", "Cita de Cierre", "Emisión de Póliza", "Póliza Pagada"]:
        if col not in tabla_asesores.columns:
            tabla_asesores[col] = 0
            
    st.dataframe(tabla_asesores.style.highlight_max(axis=0, color='#26a69a'), use_container_width=True)

    # 4. HISTORIAL RECIENTE
    with st.expander("📄 Ver últimos 10 movimientos"):
        st.table(df.sort_values(by='fecha', ascending=False).head(10)[['asesor', 'etapa', 'fecha']])

else:
    st.info("👋 ¡Bienvenido! Ingresa el primer registro en el panel de la izquierda para comenzar.")
