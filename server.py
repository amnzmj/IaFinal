from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir CORS para el dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista para guardar los datos de los vehículos
vehiculos_detectados = []

class Vehiculo(BaseModel):
    id: int
    tipo: str
    carril: str
    velocidad: float
    cambio_carril: bool

@app.post("/vehiculos")
def guardar_vehiculo(vehiculo: Vehiculo):
    vehiculos_detectados.append(vehiculo)
    return {"mensaje": "Vehiculo recibido"}

@app.get("/vehiculos")
def obtener_vehiculos():
    return vehiculos_detectados
