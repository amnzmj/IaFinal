import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Dashboard Vehicular", layout="wide")

# Auto-refresh cada 2 segundos (2000 ms)
st_autorefresh(interval=2000, key="refresh")

st.title("🚗 Dashboard de Vehículos Detectados")

API_URL = "http://localhost:8000/vehiculos"

def cargar_datos():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
    return pd.DataFrame()

# Cargar datos desde API
df = cargar_datos()

# Mostrar datos
if df.empty:
    st.warning("No hay vehículos detectados aún...")
else:
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Estadísticas del tráfico")

    col1, col2, col3 = st.columns(3)

    with col1:
        total = len(df)
        st.metric("Vehículos detectados", total)

    with col2:
        velocidad_promedio = df["velocidad"].mean()
        st.metric("Velocidad promedio (km/h)", round(velocidad_promedio, 2))

    with col3:
        cambios_carril = df["cambio_carril"].sum()
        st.metric("Cambios de carril", cambios_carril)
