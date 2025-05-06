# app/models/product.py
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, index=True)
    platform = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    price = Column(Numeric(10, 2))  # Maior precisão para valores monetários
    sale_price = Column(Numeric(10, 2), nullable=True)
    image_url = Column(String)
    product_url = Column(String)
    affiliate_url = Column(String, nullable=True)
    category = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    available = Column(Boolean, default=True)
    # Novo relacionamento com AffiliateStore
    affiliate_store_id = Column(Integer, ForeignKey('affiliate_stores.id'), nullable=True)
    affiliate_store = relationship('AffiliateStore', backref="products")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Product {self.title}>"