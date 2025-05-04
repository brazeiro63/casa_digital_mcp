from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate
from app.services.affiliate_service import AffiliateService

router = APIRouter()
affiliate_service = AffiliateService()

@router.post("/products/{platform}/", response_model=Dict[str, Any])
async def sync_products(
    platform: str,
    query: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    category: str = None,
    limit: int = 50,
):
    """
    Sincroniza produtos de uma plataforma para o banco de dados local.
    """
    # Verificar se a plataforma é suportada
    try:
        affiliate_service.get_client(platform)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")
    
    # Iniciar sincronização em segundo plano
    background_tasks.add_task(
        sync_products_task,
        platform=platform,
        query=query,
        category=category,
        limit=limit,
        db=db
    )
    
    return {
        "message": "Product synchronization started",
        "platform": platform,
        "query": query,
        "category": category,
        "limit": limit
    }

async def sync_products_task(
    platform: str,
    query: str,
    category: str,
    limit: int,
    db: Session
):
    """
    Tarefa em segundo plano para sincronizar produtos.
    """
    try:
        # Buscar produtos na plataforma
        products = await affiliate_service.search_products(platform, query, category=category, limit=limit)
        
        # Sincronizar com o banco de dados
        for product_data in products:
            # Verificar se o produto já existe
            existing_product = db.query(Product).filter(
                Product.external_id == product_data.external_id,
                Product.platform == platform
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