# app/api/api.py
from fastapi import APIRouter

from app.api.endpoints import admin, products, sync, affiliate_links, affiliate_stores

api_router = APIRouter()
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(affiliate_links.router, prefix="/affiliate-links", tags=["affiliate-links"])
api_router.include_router(affiliate_stores.router, prefix="/affiliate-stores", tags=["affiliate-stores"])