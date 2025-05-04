from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, index=True)
    platform = Column(String, index=True)  # mercadolivre, amazon, etc.
    title = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    sale_price = Column(Float, nullable=True)
    image_url = Column(String, nullable=True)
    product_url = Column(String)
    category = Column(String, index=True)
    brand = Column(String, index=True, nullable=True)
    available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Product {self.title}>"