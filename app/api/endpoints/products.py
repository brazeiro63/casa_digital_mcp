from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.schemas.product import Product as ProductSchema, ProductCreate, ProductUpdate
from app.services.affiliate_service import AffiliateService

router = APIRouter()

# Manter os endpoints existentes...

@router.get("/search/", response_model=Dict[str, List[ProductSchema]])
async def search_products_all_platforms(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Busca produtos em todas as plataformas suportadas.
    """
    affiliate_service = AffiliateService(db)
    results = await affiliate_service.search_products_all_platforms(q, limit=limit)
    return results

@router.get("/search/{platform}/", response_model=List[ProductSchema])
async def search_products(
    platform: str,
    q: str = Query(..., min_length=2),
    category: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Busca produtos em uma plataforma específica.
    """
    affiliate_service = AffiliateService(db)
    results = await affiliate_service.search_products(platform, q, category=category, limit=limit)
    return results

@router.get("/external/{platform}/{product_id}", response_model=ProductSchema)
async def get_external_product(
    platform: str,
    product_id: str,
    db: Session = Depends(get_db),
):
    """
    Obtém detalhes de um produto externo específico.
    """
    affiliate_service = AffiliateService(db)
    product = await affiliate_service.get_product_details(platform, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/categories/{platform}/", response_model=List[Dict[str, Any]])
async def get_product_categories(
    platform: str,
    db: Session = Depends(get_db),
):
    """
    Obtém as categorias de produtos disponíveis na plataforma.
    """
    affiliate_service = AffiliateService(db)
    categories = await affiliate_service.get_product_categories(platform)
    return categories

@router.get("/{product_id}", response_model=ProductSchema)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    affiliate_service = AffiliateService(db)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Usar URL de afiliado se disponível
    response_data = product.__dict__.copy()
    if product.affiliate_url:
        response_data["product_url"] = product.affiliate_url
    
    return response_data