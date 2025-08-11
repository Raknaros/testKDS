# Archivo: main.py
import asyncio
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from typing import List
import json

app = FastAPI()


# --------------------------------------------------------------------------
# 1. GESTOR DE CONEXIONES WEBSOCKET
# Este objeto mantendrá una lista de todos los dashboards conectados.
# --------------------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_json(self, data: dict):
        # Envía datos JSON a todos los dashboards conectados.
        for connection in self.active_connections:
            await connection.send_text(json.dumps(data))


manager = ConnectionManager()


# --------------------------------------------------------------------------
# 2. ENDPOINT PARA EL DASHBOARD EN TIEMPO REAL
# Aquí es donde tu frontend (la página web) se conecta para recibir actualizaciones.
# --------------------------------------------------------------------------
@app.websocket("/ws/orders")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("Dashboard conectado.")
    try:
        while True:
            # Mantenemos la conexión abierta.
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Dashboard desconectado.")


# --------------------------------------------------------------------------
# 3. ENDPOINT PARA RECIBIR PEDIDOS (DE TELEGRAM)
# Este es el webhook que Telegram llamaría.
# --------------------------------------------------------------------------
@app.post("/webhook/telegram")
async def receive_order(request: Request):
    # En un caso real, aquí recibirías los datos del bot de Telegram.
    # El Agente ADK procesaría el mensaje para extraer los detalles del pedido.
    # Luego, guardaría el pedido en la base de datos PostgreSQL.

    # --- SIMULACIÓN DEL PROCESO ---
    print("Recibido nuevo pedido desde el webhook...")

    # Suponemos que el agente procesó el pedido y generó este diccionario:
    new_order_data = {
        "order_id": f"ORD-00{await request.json()}",  # Simulación de ID de orden
        "details": f"Pedido simulado desde Telegram {await request.json()}",
        "scheduled_time": "12:00"  # La columna donde debe aparecer
    }

    # Esto es lo más importante: después de guardar en la DB, notificamos a los dashboards.
    await manager.broadcast_json(new_order_data)

    print(f"Pedido {new_order_data['order_id']} notificado a los dashboards.")

    return {"status": "ok", "message": "Pedido recibido y notificado."}