from fastapi import APIRouter

from app.api.endpoints import products, sync

api_router = APIRouter()
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])