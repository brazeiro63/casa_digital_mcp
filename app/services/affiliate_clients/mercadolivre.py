import httpx
import re
from typing import Dict, List, Optional, Any
import logging
from urllib.parse import quote, urlparse, parse_qs, urlencode

from app.services.affiliate_clients.base import AffiliateClientBase
from app.schemas.product import ProductCreate
from app.core.config import settings
from app.core.affiliate_config import get_affiliate_config

logger = logging.getLogger(__name__)

class MercadoLivreClient(AffiliateClientBase):
    """
    Cliente para a API do Mercado Livre.
    """
    
    BASE_URL = "https://api.mercadolibre.com"
    SITE_ID = "MLB"  # MLB para Brasil
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @property
    def platform_name(self) -> str:
        return "mercadolivre"
    
    def convert_to_affiliate_link(self, product_url: str) -> str:
        """
        Converte uma URL genérica do Mercado Livre em um link de afiliado.
        
        Args:
            product_url: URL do produto
            
        Returns:
            Link de afiliado
        """
        try:
            # Obter configuração de afiliado
            config = get_affiliate_config("mercadolivre")
            if not config or not config.get("affiliate_id"):
                return product_url  # Retorna a URL original se não houver configuração
            
            # Extrair o ID do produto da URL
            product_id = self._extract_product_id(product_url)
            if not product_id:
                return product_url  # Retorna a URL original se não conseguir extrair o ID
            
            # Construir parâmetros de afiliado
            params = {
                "id": product_id,
                "platform": config.get("platform", "ml"),
                "referer": config.get("affiliate_id"),
                "utm_source": config.get("affiliate_id"),
                "utm_medium": "affiliate",
            }
            
            if config.get("campaign"):
                params["utm_campaign"] = config.get("campaign")
            
            # Construir URL de redirecionamento
            base_url = "https://www.mercadolivre.com.br/link/redirect"
            query_string = urlencode(params)
            
            return f"{base_url}?{query_string}"
        except Exception as e:
            logger.error(f"Error converting to affiliate link: {e}")
            return product_url  # Retorna a URL original em caso de erro
    
    def _extract_product_id(self, url: str) -> Optional[str]:
        """
        Extrai o ID do produto de uma URL do Mercado Livre.
        
        Args:
            url: URL do produto
            
        Returns:
            ID do produto ou None se não encontrado
        """
        try:
            # Padrão 1: URLs de produto padrão (MLB12345678)
            pattern1 = r"MLB-?(\d+)"
            match1 = re.search(pattern1, url)
            if match1:
                return f"MLB{match1.group(1)}"
            
            # Padrão 2: URLs com ID no parâmetro de consulta
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if "id" in query_params:
                return query_params["id"][0]
            
            # Padrão 3: URLs de produto no formato /p/MLB12345678
            pattern3 = r"/p/(MLB\d+)"
            match3 = re.search(pattern3, url)
            if match3:
                return match3.group(1)
            
            return None
        except Exception as e:
            logger.error(f"Error extracting product ID: {e}")
            return None
    
    async def search_products(self, query: str, category: Optional[str] = None, limit: int = 20) -> List[ProductCreate]:
        """
        Busca produtos no Mercado Livre.
        
        Args:
            query: Termo de busca
            category: ID da categoria (opcional)
            limit: Número máximo de resultados
            
        Returns:
            Lista de produtos encontrados
        """
        try:
            # Construir URL de busca
            search_url = f"{self.BASE_URL}/sites/{self.SITE_ID}/search?q={quote(query)}&limit={limit}"
            
            if category:
                search_url += f"&category={category}"
            
            # Adicionar token de acesso se disponível
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            # Fazer requisição
            response = await self.client.get(search_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            products = []
            
            for item in data.get("results", []):
                try:
                    # Converter URL genérica para link de afiliado
                    product_url = item["permalink"]
                    affiliate_url = self.convert_to_affiliate_link(product_url)
                    
                    # Converter para o formato do nosso modelo
                    product = ProductCreate(
                        external_id=item["id"],
                        platform=self.platform_name,
                        title=item["title"],
                        description=item.get("description", ""),  # Descrição completa requer outra chamada
                        price=float(item["price"]),
                        sale_price=float(item.get("original_price", 0)) if item.get("original_price") else None,
                        image_url=item["thumbnail"],
                        product_url=affiliate_url,  # Use o link de afiliado
                        category=item.get("category_id", ""),
                        brand=None,  # Requer outra chamada para obter
                        available=item.get("available_quantity", 0) > 0
                    )
                    products.append(product)
                except Exception as e:
                    logger.error(f"Error processing product {item.get('id')}: {e}")
            
            return products
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during search: {e}")
            return []
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    async def get_product_details(self, product_id: str) -> Optional[ProductCreate]:
        """
        Obtém detalhes de um produto específico.
        
        Args:
            product_id: ID do produto no Mercado Livre
            
        Returns:
            Detalhes do produto ou None se não encontrado
        """
        try:
            # Construir URL do produto
            product_url = f"{self.BASE_URL}/items/{product_id}"
            
            # Adicionar token de acesso se disponível
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            # Fazer requisição
            response = await self.client.get(product_url, headers=headers)
            response.raise_for_status()
            
            item = response.json()
            
            # Obter descrição completa
            description = await self._get_product_description(product_id)
            
            # Converter URL genérica para link de afiliado
            original_url = item["permalink"]
            affiliate_url = self.convert_to_affiliate_link(original_url)
            
            # Converter para o formato do nosso modelo
            product = ProductCreate(
                external_id=item["id"],
                platform=self.platform_name,
                title=item["title"],
                description=description or item.get("subtitle", ""),
                price=float(item["price"]),
                sale_price=float(item.get("original_price", 0)) if item.get("original_price") else None,
                image_url=item["thumbnail"],
                product_url=affiliate_url,  # Use o link de afiliado
                category=item.get("category_id", ""),
                brand=None,  # Tentar extrair da descrição ou atributos
                available=item.get("available_quantity", 0) > 0
            )
            
            return product
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting product details: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return None
    
    async def _get_product_description(self, product_id: str) -> Optional[str]:
        """
        Obtém a descrição completa de um produto.
        
        Args:
            product_id: ID do produto
            
        Returns:
            Descrição do produto ou None se não encontrada
        """
        try:
            # Construir URL da descrição
            description_url = f"{self.BASE_URL}/items/{product_id}/description"
            
            # Adicionar token de acesso se disponível
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            # Fazer requisição
            response = await self.client.get(description_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get("plain_text", "")
            
        except Exception as e:
            logger.error(f"Error getting product description: {e}")
            return None
    
    async def get_product_categories(self) -> List[Dict[str, Any]]:
        """
        Obtém as categorias de produtos disponíveis no Mercado Livre.
        
        Returns:
            Lista de categorias
        """
        try:
            # Construir URL de categorias
            categories_url = f"{self.BASE_URL}/sites/{self.SITE_ID}/categories"
            
            # Adicionar token de acesso se disponível
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            # Fazer requisição
            response = await self.client.get(categories_url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    async def get_category_details(self, category_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém detalhes de uma categoria específica.
        
        Args:
            category_id: ID da categoria
            
        Returns:
            Detalhes da categoria ou None se não encontrada
        """
        try:
            # Construir URL da categoria
            category_url = f"{self.BASE_URL}/categories/{category_id}"
            
            # Adicionar token de acesso se disponível
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            # Fazer requisição
            response = await self.client.get(category_url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error getting category details: {e}")
            return None
    
    async def get_trending_products(self, category: Optional[str] = None, limit: int = 20) -> List[ProductCreate]:
        """
        Obtém produtos em tendência no Mercado Livre.
        
        Args:
            category: ID da categoria (opcional)
            limit: Número máximo de resultados
            
        Returns:
            Lista de produtos em tendência
        """
        try:
            # Construir URL de tendências
            trending_url = f"{self.BASE_URL}/trends/{self.SITE_ID}"
            
            if category:
                trending_url += f"/category/{category}"
            
            trending_url += f"?limit={limit}"
            
            # Adicionar token de acesso se disponível
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            # Fazer requisição
            response = await self.client.get(trending_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            products = []
            
            for trend in data:
                try:
                    # Obter detalhes do produto
                    product_id = trend.get("id") or trend.get("product_id")
                    if product_id:
                        product_details = await self.get_product_details(product_id)
                        if product_details:
                            products.append(product_details)
                except Exception as e:
                    logger.error(f"Error processing trending product: {e}")
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting trending products: {e}")
            return []
    
    async def close(self):
        """
        Fecha o cliente HTTP.
        """
        await self.client.aclose()