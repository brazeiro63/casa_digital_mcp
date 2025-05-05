# app/api/api.py
from fastapi import APIRouter

from app.api.endpoints import products, sync, affiliate_links, admin

api_router = APIRouter()
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(affiliate_links.router, prefix="/affiliate-links", tags=["affiliate-links"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])