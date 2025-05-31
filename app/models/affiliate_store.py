# app/models/affiliate_store.py
from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, func
from app.db.session import Base

class AffiliateStore(Base):
    __tablename__ = "affiliate_stores"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    platform = Column(String, index=True, nullable=False)  # mercadolivre, amazon, etc.
    url = Column(String(255), index=True, nullable=True)  # Nova coluna para a URL da loja
    api_credentials = Column(JSON, nullable=False)  # Armazena credenciais de forma segura
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())