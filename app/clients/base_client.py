# app/clients/base_client.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class BaseMarketplaceClient(ABC):
    """Base client for marketplace integrations."""
    
    def __init__(self, credentials: Dict[str, str]):
        """Initialize with API credentials."""
        self.credentials = credentials
    
    @abstractmethod
    async def search_products(self, query: str, category: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for products in the marketplace."""
        pass
    
    @abstractmethod
    async def generate_affiliate_link(self, product_url: str) -> str:
        """Generate an affiliate link for a product."""
        pass
    
    @abstractmethod
    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific product."""
        pass
    