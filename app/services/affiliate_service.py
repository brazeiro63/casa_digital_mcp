from typing import Dict, List, Optional, Any
import logging

from app.services.affiliate_clients import get_affiliate_client
from app.services.affiliate_clients.base import AffiliateClientBase
from app.schemas.product import ProductCreate
from app.services.cache import cache

logger = logging.getLogger(__name__)

class AffiliateService:
    """
    Serviço para gerenciar e interagir com diferentes plataformas de afiliados.
    """
    
    def __init__(self):
        self.clients: Dict[str, AffiliateClientBase] = {}
    
    def get_client(self, platform: str) -> AffiliateClientBase:
        """
        Obtém um cliente para a plataforma especificada, criando-o se necessário.
        
        Args:
            platform: Nome da plataforma
            
        Returns:
            Cliente para a plataforma
        """
        if platform not in self.clients:
            try:
                self.clients[platform] = get_affiliate_client(platform)
            except ValueError as e:
                logger.error(f"Error creating affiliate client: {e}")
                raise
        
        return self.clients[platform]
    
    async def search_products_all_platforms(self, query: str, limit: int = 20) -> Dict[str, List[ProductCreate]]:
        """
        Busca produtos em todas as plataformas suportadas.
        
        Args:
            query: Termo de busca
            limit: Número máximo de resultados por plataforma
            
        Returns:
            Dicionário com resultados por plataforma
        """
        # Verificar cache
        cache_key = f"search:all:{query}:{limit}"
        cached_results = await cache.get(cache_key)
        if cached_results:
            return cached_results
        
        results: Dict[str, List[ProductCreate]] = {}
        
        for platform in ["mercadolivre"]:  # Adicionar outras plataformas aqui
            try:
                client = self.get_client(platform)
                products = await client.search_products(query, limit=limit)
                
                # Converter para dicionários para armazenar no cache
                results[platform] = [p.model_dump() for p in products]
            except Exception as e:
                logger.error(f"Error searching products on {platform}: {e}")
                results[platform] = []
        
        # Armazenar no cache por 30 minutos
        await cache.set(cache_key, results, expire=1800)
        
        return results
    
    async def search_products(self, platform: str, query: str, category: Optional[str] = None, limit: int = 20) -> List[ProductCreate]:
        """
        Busca produtos em uma plataforma específica.
        
        Args:
            platform: Nome da plataforma
            query: Termo de busca
            category: Categoria opcional para filtrar
            limit: Número máximo de resultados
            
        Returns:
            Lista de produtos encontrados
        """
        # Verificar cache
        cache_key = f"search:{platform}:{query}:{category}:{limit}"
        cached_results = await cache.get(cache_key)
        if cached_results:
            # Converter de volta para objetos ProductCreate
            return [ProductCreate(**item) for item in cached_results]
        
        try:
            client = self.get_client(platform)
            products = await client.search_products(query, category=category, limit=limit)
            
            # Armazenar no cache por 30 minutos
            await cache.set(cache_key, [p.model_dump() for p in products], expire=1800)
            
            return products
        except Exception as e:
            logger.error(f"Error searching products on {platform}: {e}")
            return []
    
    async def get_product_details(self, platform: str, product_id: str) -> Optional[ProductCreate]:
        """
        Obtém detalhes de um produto específico.
        
        Args:
            platform: Nome da plataforma
            product_id: ID do produto na plataforma
            
        Returns:
            Detalhes do produto ou None se não encontrado
        """
        # Verificar cache
        cache_key = f"product:{platform}:{product_id}"
        cached_product = await cache.get(cache_key)
        if cached_product:
            return ProductCreate(**cached_product)
        
        try:
            client = self.get_client(platform)
            product = await client.get_product_details(product_id)
            
            if product:
                # Armazenar no cache por 1 hora
                await cache.set(cache_key, product.model_dump(), expire=3600)
            
            return product
        except Exception as e:
            logger.error(f"Error getting product details from {platform}: {e}")
            return None
    
    async def get_product_categories(self, platform: str) -> List[Dict[str, Any]]:
        """
        Obtém as categorias de produtos disponíveis na plataforma.
        
        Args:
            platform: Nome da plataforma
            
        Returns:
            Lista de categorias
        """
        # Verificar cache
        cache_key = f"categories:{platform}"
        cached_categories = await cache.get(cache_key)
        if cached_categories:
            return cached_categories
        
        try:
            client = self.get_client(platform)
            categories = await client.get_product_categories()
            
            # Armazenar no cache por 24 horas
            await cache.set(cache_key, categories, expire=86400)
            
            return categories
        except Exception as e:
            logger.error(f"Error getting categories from {platform}: {e}")
            return []
    
    async def close(self):
        """
        Fecha todos os clientes.
        """
        for client in self.clients.values():
            await client.close()