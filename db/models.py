"""Pedidos Ya data model definition."""

from sqlalchemy import Column, Date, Float, String, UniqueConstraint, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PedidosYa(Base):
    """Pedidos Ya data model."""

    __tablename__ = "pedidosya_orders"

    __table_args__ = (UniqueConstraint("id"),)

    id = Column(Integer)
    date = Column(Date)
    total_amount = Column(Float)
    subtotal_amount = Column(Float)
    tip_amount = Column(Float)
    shipping_amount = Column(Float)
    discount_amount = Column(Float)
    payment_method = Column(String)

    __mapper_args__ = {"primary_key": [id]}

    def __init__(
        self,
        id,
        date,
        total_amount,
        subtotal_amount,
        tip_amount,
        shipping_amount,
        discount_amount,
        payment_method,
    ):
        self.id = id
        self.date = date
        self.total_amount = total_amount
        self.subtotal_amount = subtotal_amount
        self.tip_amount = tip_amount
        self.shipping_amount = shipping_amount
        self.discount_amount = discount_amount
        self.payment_method = payment_method

    def __repr__(self):
        return f"""
        <StockValue(id='{self.id}', 
                    date='{self.date}', 
                    total_amount='{self.total_amount}', 
                    subtotal_amount='{self.subtotal_amount}, 
                    tip_amount='{self.tip_amount}', 
                    shipping_amount='{self.shipping_amount}',
                    discount_amount='{self.discount_amount}',
                    payment_method='{self.payment_method}'
        )>"""
