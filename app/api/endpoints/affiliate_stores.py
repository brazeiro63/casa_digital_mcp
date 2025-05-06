# app/api/endpoints/affiliate_stores.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.affiliate_store import AffiliateStore
from app.schemas.affiliate_store import AffiliateStoreCreate, AffiliateStoreUpdate, AffiliateStoreInDB

router = APIRouter()

@router.post("/", response_model=AffiliateStoreInDB)
def create_affiliate_store(
    store: AffiliateStoreCreate,
    db: Session = Depends(get_db)
):
    """Create a new affiliate store."""
    db_store = AffiliateStore(**store.model_dump())
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

@router.get("/", response_model=List[AffiliateStoreInDB])
def read_affiliate_stores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all affiliate stores."""
    stores = db.query(AffiliateStore).offset(skip).limit(limit).all()
    return stores

@router.get("/{store_id}", response_model=AffiliateStoreInDB)
def read_affiliate_store(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific affiliate store."""
    db_store = db.query(AffiliateStore).filter(AffiliateStore.id == store_id).first()
    if db_store is None:
        raise HTTPException(status_code=404, detail="Affiliate store not found")
    return db_store

@router.put("/{store_id}", response_model=AffiliateStoreInDB)
def update_affiliate_store(
    store_id: int,
    store: AffiliateStoreUpdate,
    db: Session = Depends(get_db)
):
    """Update an affiliate store."""
    db_store = db.query(AffiliateStore).filter(AffiliateStore.id == store_id).first()
    if db_store is None:
        raise HTTPException(status_code=404, detail="Affiliate store not found")
    
    update_data = store.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_store, key, value)
    
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store

@router.delete("/{store_id}", response_model=AffiliateStoreInDB)
def delete_affiliate_store(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Delete an affiliate store."""
    db_store = db.query(AffiliateStore).filter(AffiliateStore.id == store_id).first()
    if db_store is None:
        raise HTTPException(status_code=404, detail="Affiliate store not found")
    
    db.delete(db_store)
    db.commit()
    return db_store