# app/schemas/affiliate_store.py
from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class AffiliateStoreBase(BaseModel):
    name: str
    platform: str
    active: bool = True

class AffiliateStoreCreate(AffiliateStoreBase):
    api_credentials: Dict[str, str] = Field(..., description="API credentials for the platform")

class AffiliateStoreUpdate(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None
    api_credentials: Optional[Dict[str, str]] = None
    active: Optional[bool] = None

class AffiliateStoreInDB(AffiliateStoreBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True