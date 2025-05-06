# app/api/endpoints/sync.py
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate
from app.services.affiliate_service import AffiliateService

router = APIRouter()

def get_affiliate_service(db: Session = Depends(get_db)):
    return AffiliateService(db)

@router.post("/stores/{store_id}/products/", response_model=Dict[str, Any])
async def sync_products(
    store_id: int,
    query: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    affiliate_service: AffiliateService = Depends(get_affiliate_service),
    category: Optional[str] = None,
    limit: int = 50,
):
    """
    Synchronize products from an affiliate store to the local database.
    """
    # Verificar se a loja existe
    try:
        affiliate_service.get_client(store_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Iniciar sincronização em segundo plano
    background_tasks.add_task(
        sync_products_task,
        store_id=store_id,
        query=query,
        category=category,
        limit=limit,
        db=db,
        affiliate_service=affiliate_service
    )
    
    return {
        "message": "Product synchronization started",
        "store_id": store_id,
        "query": query,
        "category": category,
        "limit": limit
    }

async def sync_products_task(
    store_id: int,
    query: str,
    category: Optional[str],
    limit: int,
    db: Session,
    affiliate_service: AffiliateService
):
    """
    Background task to synchronize products.
    """
    try:
        # Buscar produtos na loja afiliada
        products = await affiliate_service.search_products(
            store_id=store_id,
            query=query,
            category=category,
            limit=limit
        )
        
        # Sincronizar com o banco de dados
        for product_data in products:
            # Verificar se o produto já existe
            existing_product = db.query(Product).filter(
                Product.external_id == product_data.external_id,
                Product.platform == product_data.platform
            ).first()
            
            if existing_product:
                # Atualizar produto existente
                for key, value in product_data.model_dump().items():
                    setattr(existing_product, key, value)
                db.add(existing_product)
            else:
                # Criar novo produto
                product = Product(**product_data.model_dump())
                db.add(product)
        
        db.commit()
    except Exception as e:
        db.rollback()
        # Log do erro
        print(f"Error syncing products: {e}")