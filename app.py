import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.title("🚀 Sistema de Seguimiento")
# Aquí iría el resto del código que te pasé antes...
st.write("¡Si ves esto, tu app funciona!")
""")

# 3. Lanzamos la app (esto te dará un link temporal)
from pyngrok import ngrok
public_url = ngrok.connect(8501).public_url
print(f"HAZ CLIC AQUÍ PARA VER TU APP: {public_url}")
!streamlit run app.py &>/dev/null &
