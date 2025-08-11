from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from datetime import datetime
from app.database.connection import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    customer_phone = Column(String)
    items = Column(JSON)  # Lista de items del pedido
    total_amount = Column(Float)
    special_instructions = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending, preparing, ready, delivered
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_time = Column(String, nullable=True)  # Hora programada para el pedido

    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "items": self.items,
            "total_amount": self.total_amount,
            "special_instructions": self.special_instructions,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "scheduled_time": self.scheduled_time
        }
