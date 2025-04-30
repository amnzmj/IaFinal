# Importamos las librerías necesarias
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

# Inicializamos la aplicación FastAPI
app = FastAPI()

# Configuración de CORS (Cross-Origin Resource Sharing)
# Esto permite que la API sea accesible desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite solicitudes desde cualquier origen
    allow_methods=["*"],  # Permite cualquier método HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite cualquier tipo de encabezado
)

# Lista para almacenar los vehículos detectados
# En una implementación real, probablemente se usaría una base de datos en lugar de una lista
vehiculos_detectados = []

# Definimos el modelo de datos para un vehículo utilizando Pydantic
class Vehiculo(BaseModel):
    id: int  # Identificador único del vehículo (número entero)
    tipo: str  # Tipo de vehículo (cadena de texto)
    carril: str  # Carril en el que se encuentra el vehículo (cadena de texto)
    velocidad: float  # Velocidad del vehículo (número flotante)
    cambio_carril: bool  # Indica si el vehículo cambió de carril (booleano)

# Endpoint POST para recibir información de vehículos
# Este endpoint recibe datos de vehículos en formato JSON y los guarda en la lista
@app.post("/vehiculos")
def guardar_vehiculo(vehiculo: Vehiculo):
    """
    Este endpoint recibe un objeto Vehiculo a través de una solicitud POST
    y lo agrega a la lista 'vehiculos_detectados'.
    """
    vehiculos_detectados.append(vehiculo)  # Agrega el vehículo a la lista
    return {"mensaje": "Vehiculo recibido"}  # Respuesta confirmando la recepción del vehículo

# Endpoint GET para obtener la lista de vehículos detectados
# Este endpoint devuelve la lista de todos los vehículos recibidos a través de solicitudes POST
@app.get("/vehiculos")
def obtener_vehiculos():
    """
    Este endpoint devuelve la lista de todos los vehículos almacenados en 'vehiculos_detectados'.
    """
    return vehiculos_detectados  # Devuelve la lista de vehículos detectados
