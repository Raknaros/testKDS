from fastapi import WebSocket
from typing import List
from app.models.order import Order

class DashboardManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_order(self, order_data: dict):
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_json(order_data)
            except:
                disconnected.append(connection)

        # Limpiar conexiones cerradas
        for conn in disconnected:
            self.active_connections.remove(conn)

dashboard_manager = DashboardManager()

def get_dashboard_manager() -> DashboardManager:
    return dashboard_manager
