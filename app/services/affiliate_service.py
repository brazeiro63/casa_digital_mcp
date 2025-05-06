# app/services/affiliate_service.py
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models.affiliate_store import AffiliateStore
from app.clients.mercadolivre_client import MercadoLivreClient
from app.schemas.product import ProductCreate

class AffiliateService:
    """Service for managing affiliate stores and products."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
        self.clients = {}
        self._load_clients()
    
    def _load_clients(self):
        """Load clients for active affiliate stores."""
        stores = self.db.query(AffiliateStore).filter(AffiliateStore.active == True).all()
        
        for store in stores:
            if store.platform == "mercadolivre":
                self.clients[store.id] = MercadoLivreClient(store.api_credentials)
            # Adicionar mais plataformas conforme necessário
    
    def get_client(self, store_id: int):
        """Get client for a specific store."""
        if store_id not in self.clients:
            # Tentar carregar o cliente se não estiver carregado
            store = self.db.query(AffiliateStore).filter(
                AffiliateStore.id == store_id,
                AffiliateStore.active == True
            ).first()
            
            if not store:
                raise ValueError(f"Store with ID {store_id} not found or not active")
            
            if store.platform == "mercadolivre":
                self.clients[store.id] = MercadoLivreClient(store.api_credentials)
            # Adicionar mais plataformas conforme necessário
        
        return self.clients[store_id]
    
    async def search_products(self, store_id: int, query: str, **kwargs) -> List[ProductCreate]:
        """Search for products in a specific store."""
        client = self.get_client(store_id)
        products_data = await client.search_products(query, **kwargs)
        
        # Converter para schema ProductCreate
        products = [ProductCreate(**product_data) for product_data in products_data]
        return products
    
    async def generate_affiliate_link(self, store_id: int, product_url: str) -> str:
        """Generate an affiliate link for a product."""
        client = self.get_client(store_id)
        return await client.generate_affiliate_link(product_url)
    
    async def get_product_details(self, store_id: int, product_id: str) -> ProductCreate:
        """Get detailed information about a specific product."""
        client = self.get_client(store_id)
        product_data = await client.get_product_details(product_id)
        return ProductCreate(**product_data)