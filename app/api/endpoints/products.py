from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.schemas.product import Product as ProductSchema, ProductCreate, ProductUpdate
from app.services.affiliate_service import AffiliateService

router = APIRouter()
affiliate_service = AffiliateService()

# Manter os endpoints existentes...

@router.get("/search/", response_model=Dict[str, List[ProductSchema]])
async def search_products_all_platforms(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=50),
):
    """
    Busca produtos em todas as plataformas suportadas.
    """
    results = await affiliate_service.search_products_all_platforms(q, limit=limit)
    return results

@router.get("/search/{platform}/", response_model=List[ProductSchema])
async def search_products(
    platform: str,
    q: str = Query(..., min_length=2),
    category: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
):
    """
    Busca produtos em uma plataforma específica.
    """
    results = await affiliate_service.search_products(platform, q, category=category, limit=limit)
    return results

@router.get("/external/{platform}/{product_id}", response_model=ProductSchema)
async def get_external_product(
    platform: str,
    product_id: str,
):
    """
    Obtém detalhes de um produto externo específico.
    """
    product = await affiliate_service.get_product_details(platform, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/categories/{platform}/", response_model=List[Dict[str, Any]])
async def get_product_categories(
    platform: str,
):
    """
    Obtém as categorias de produtos disponíveis na plataforma.
    """
    categories = await affiliate_service.get_product_categories(platform)
    return categories