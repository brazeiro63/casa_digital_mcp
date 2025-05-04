from typing import Dict, Any

# Configurações de afiliados
AFFILIATE_CONFIG = {
    "mercadolivre": {
        "affiliate_id": "YOUR_AFFILIATE_ID",  # Substitua pelo seu ID de afiliado
        "campaign": "casadigital",
        "platform": "ml"
    }
    # Adicione outras plataformas conforme necessário
}

def get_affiliate_config(platform: str) -> Dict[str, Any]:
    """
    Obtém a configuração de afiliado para uma plataforma.
    
    Args:
        platform: Nome da plataforma
        
    Returns:
        Configuração de afiliado
    """
    return AFFILIATE_CONFIG.get(platform, {})