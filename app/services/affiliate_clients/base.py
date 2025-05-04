from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from app.schemas.product import ProductCreate

class AffiliateClientBase(ABC):
    """
    Interface base para todos os clientes de afiliados.
    Todas as implementações específicas de plataforma devem herdar desta classe.
    """
    
    @abstractmethod
    async def search_products(self, query: str, category: Optional[str] = None, limit: int = 20) -> List[ProductCreate]:
        """
        Busca produtos na plataforma de afiliados.
        
        Args:
            query: Termo de busca
            category: Categoria opcional para filtrar
            limit: Número máximo de resultados
            
        Returns:
            Lista de produtos encontrados
        """
        pass
    
    @abstractmethod
    async def get_product_details(self, product_id: str) -> ProductCreate:
        """
        Obtém detalhes de um produto específico.
        
        Args:
            product_id: ID do produto na plataforma
            
        Returns:
            Detalhes do produto
        """
        pass
    
    @abstractmethod
    async def get_product_categories(self) -> List[Dict[str, Any]]:
        """
        Obtém as categorias de produtos disponíveis na plataforma.
        
        Returns:
            Lista de categorias
        """
        pass
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """
        Nome da plataforma de afiliados.
        
        Returns:
            Nome da plataforma
        """
        pass