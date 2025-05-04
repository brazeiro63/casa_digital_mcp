from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl

class ProductBase(BaseModel):
    external_id: str
    platform: str
    title: str
    description: str
    price: float
    sale_price: Optional[float] = None
    image_url: Optional[str] = None
    product_url: str
    category: str
    brand: Optional[str] = None
    available: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    sale_price: Optional[float] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    available: Optional[bool] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True