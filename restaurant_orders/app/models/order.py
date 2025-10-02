from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime

from app.database.connection import Base

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, name="cliente_test")
    delivery_time = Column(String, name="hora_entrega")
    destination = Column(String, name="destino")
    total_amount = Column(Float, name="importe_total")
    observations = Column(Text, name="observaciones")
    status = Column(String, default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    items = relationship("OrderItem", back_populates="order")
    payment = relationship("Payment", uselist=False, back_populates="order")

    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "delivery_time": self.delivery_time,
            "destination": self.destination,
            "total_amount": self.total_amount,
            "observations": self.observations,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "items": [item.to_dict() for item in self.items],
            "payment": self.payment.to_dict() if self.payment else None,
        }

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), name="v_pedido_id")
    product_name = Column(String, name="v_producto_test")
    quantity = Column(Integer, name="v_cantidad")
    price = Column(Float, name="v_precio")
    notes = Column(Text, name="v_notas")

    order = relationship("Order", back_populates="items")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "price": self.price,
            "notes": self.notes,
        }

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), name="v_pedido_id")
    method = Column(String, name="v_metodo")
    amount = Column(Float, name="v_importe")
    status = Column(String, name="v_estado")
    payment_date = Column(DateTime, name="v_fecha_hora", default=datetime.datetime.utcnow)

    order = relationship("Order", back_populates="payment")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "method": self.method,
            "amount": self.amount,
            "status": self.status,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
        }
