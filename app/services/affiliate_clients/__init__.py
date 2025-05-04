from typing import Dict, Type

from app.services.affiliate_clients.base import AffiliateClientBase
from app.services.affiliate_clients.mercadolivre import MercadoLivreClient

# Registro de clientes disponíveis
AFFILIATE_CLIENTS: Dict[str, Type[AffiliateClientBase]] = {
    "mercadolivre": MercadoLivreClient,
    # Adicionar outros clientes aqui
}

def get_affiliate_client(platform: str, **kwargs) -> AffiliateClientBase:
    """
    Factory para criar instâncias de clientes de afiliados.
    
    Args:
        platform: Nome da plataforma
        **kwargs: Argumentos adicionais para o construtor do cliente
        
    Returns:
        Instância do cliente para a plataforma especificada
        
    Raises:
        ValueError: Se a plataforma não for suportada
    """
    if platform not in AFFILIATE_CLIENTS:
        raise ValueError(f"Unsupported affiliate platform: {platform}")
    
    client_class = AFFILIATE_CLIENTS[platform]
    return client_class(**kwargs)