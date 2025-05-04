import json
from typing import Any, Optional
import redis
import logging
from datetime import timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisCache:
    """
    Serviço de cache usando Redis.
    """
    
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Obtém um valor do cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor armazenado ou None se não encontrado
        """
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting value from cache: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Armazena um valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            expire: Tempo de expiração em segundos (opcional)
            
        Returns:
            True se o valor foi armazenado com sucesso, False caso contrário
        """
        try:
            serialized = json.dumps(value)
            if expire:
                return self.redis.setex(key, expire, serialized)
            else:
                return self.redis.set(key, serialized)
        except Exception as e:
            logger.error(f"Error setting value in cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Remove um valor do cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            True se o valor foi removido com sucesso, False caso contrário
        """
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Error deleting value from cache: {e}")
            return False
    
    async def clear(self) -> bool:
        """
        Limpa todo o cache.
        
        Returns:
            True se o cache foi limpo com sucesso, False caso contrário
        """
        try:
            return self.redis.flushdb()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

# Instância global do cache
cache = RedisCache()