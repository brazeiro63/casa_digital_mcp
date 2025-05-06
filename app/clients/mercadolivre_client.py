# app/clients/mercadolivre_client.py
import httpx
from typing import Dict, List, Optional, Any
from app.clients.base_client import BaseMarketplaceClient
from app.schemas.product import ProductCreate

class MercadoLivreClient(BaseMarketplaceClient):
    """Client for Mercado Livre API."""
    
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.base_url = "https://api.mercadolibre.com"
        self.access_token = credentials.get("access_token")
    
    async def search_products(self, query: str, category: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for products in Mercado Livre."""
        url = f"{self.base_url}/sites/MLB/search"
        
        params = {
            "q": query,
            "limit": limit
        }
        
        if category:
            params["category"] = category
        
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"HTTP error during search: {response.status_code} - {response.text}")
            
            data = response.json()
            products = []
            
            for item in data.get("results", []):
                product = {
                    "external_id": item.get("id"),
                    "platform": "mercadolivre",
                    "title": item.get("title"),
                    "description": item.get("description", ""),
                    "price": item.get("price"),
                    "sale_price": item.get("original_price"),
                    "image_url": item.get("thumbnail"),
                    "product_url": item.get("permalink"),
                    "category": item.get("category_id"),
                    "brand": item.get("brand", {}).get("name", ""),
                    "available": item.get("available_quantity", 0) > 0
                }
                products.append(product)
            
            return products
    
    async def generate_affiliate_link(self, product_url: str) -> str:
        """Generate an affiliate link for a Mercado Livre product."""
        # Implementação depende da API de afiliados do Mercado Livre
        # Esta é uma implementação simplificada
        if not self.access_token:
            raise ValueError("Access token is required for generating affiliate links")
        
        url = f"{self.base_url}/affiliate/create-link"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {"url": product_url}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Error generating affiliate link: {response.status_code} - {response.text}")
            
            data = response.json()
            return data.get("affiliate_url", product_url)
    
    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific product."""
        url = f"{self.base_url}/items/{product_id}"
        
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Error getting product details: {response.status_code} - {response.text}")
            
            item = response.json()
            
            # Buscar descrição do produto
            description_url = f"{self.base_url}/items/{product_id}/description"
            description_response = await client.get(description_url, headers=headers)
            description = ""
            
            if description_response.status_code == 200:
                description = description_response.json().get("plain_text", "")
            
            product = {
                "external_id": item.get("id"),
                "platform": "mercadolivre",
                "title": item.get("title"),
                "description": description,
                "price": item.get("price"),
                "sale_price": item.get("original_price"),
                "image_url": item.get("pictures", [{}])[0].get("url", item.get("thumbnail")),
                "product_url": item.get("permalink"),
                "category": item.get("category_id"),
                "brand": item.get("attributes", [{}])[0].get("value_name", ""),
                "available": item.get("available_quantity", 0) > 0
            }
            
            return product