# Importación de las librerías necesarias
import streamlit as st  # Para crear la interfaz de usuario interactiva en Streamlit
import pandas as pd  # Para manejar y procesar datos en formato DataFrame
import requests  # Para realizar solicitudes HTTP a la API
from streamlit_autorefresh import st_autorefresh  # Para habilitar el auto-refresh de la página

# Configuración de la página de Streamlit
st.set_page_config(page_title="Dashboard Vehicular", layout="wide")  # Establece el título de la página y el diseño (ancho)

# Auto-refresh cada 2 segundos (2000 ms)
# Esto actualizará la página automáticamente cada 2 segundos para cargar los datos más recientes de la API
st_autorefresh(interval=2000, key="refresh")

# Título del dashboard
st.title("🚗 Dashboard de Vehículos Detectados")

# URL de la API desde la cual se cargan los datos
API_URL = "http://localhost:8000/vehiculos"

# Función para cargar los datos de vehículos desde la API
def cargar_datos():
    """
    Realiza una solicitud GET a la API para obtener los datos de los vehículos detectados.
    Si la solicitud es exitosa, los convierte en un DataFrame de pandas.
    Si ocurre un error, muestra un mensaje de error y devuelve un DataFrame vacío.
    """
    try:
        response = requests.get(API_URL)  # Realiza la solicitud GET a la API
        if response.status_code == 200:  # Si la solicitud es exitosa (código 200)
            return pd.DataFrame(response.json())  # Convierte la respuesta JSON en un DataFrame
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")  # Muestra un mensaje de error en caso de fallar
    return pd.DataFrame()  # Devuelve un DataFrame vacío si ocurre un error

# Cargar los datos desde la API
df = cargar_datos()

# Mostrar los datos
if df.empty:
    # Si el DataFrame está vacío (no hay vehículos), se muestra una advertencia
    st.warning("No hay vehículos detectados aún...")
else:
    # Si el DataFrame contiene datos, se muestra en una tabla
    st.dataframe(df, use_container_width=True)

    # Sección de estadísticas del tráfico
    st.subheader("📈 Estadísticas del tráfico")

    # Crear tres columnas para mostrar las estadísticas
    col1, col2, col3 = st.columns(3)

    # Estadísticas en la columna 1: Total de vehículos detectados
    with col1:
        total = len(df)  # Contamos la cantidad de vehículos en el DataFrame
        st.metric("Vehículos detectados", total)  # Muestra el total de vehículos en la interfaz

    # Estadísticas en la columna 2: Velocidad promedio de los vehículos
    with col2:
        velocidad_promedio = df["velocidad"].mean()  # Calcula la velocidad promedio de los vehículos
        st.metric("Velocidad promedio (km/h)", round(velocidad_promedio, 2))  # Muestra la velocidad promedio

    # Estadísticas en la columna 3: Total de cambios de carril
    with col3:
        cambios_carril = df["cambio_carril"].sum()  # Suma la cantidad de cambios de carril (True = 1, False = 0)
        st.metric("Cambios de carril", cambios_carril)  # Muestra el número total de cambios de carril
