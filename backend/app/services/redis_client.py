import redis
import os
import json
import hashlib
import logging
from typing import Optional, Any, Dict
from datetime import datetime

# Konfiguracja logowania dla Redis
logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.client = None
        self.cache_version = "v1.0"  # Zwiększaj przy zmianach w logice analizy
        self.max_file_size_for_cache = 50 * 1024 * 1024  # 50MB limit
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_errors': 0
        }
        
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            self.client = redis.from_url(redis_url, decode_responses=True)
            # Test połączenia
            self.client.ping()
            logger.info("Redis client initialized successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed, will work without cache: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Sprawdza czy Redis jest dostępny"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False
    
    def should_cache_file(self, file_size: int) -> bool:
        """Określa czy plik powinien być cache'owany na podstawie rozmiaru"""
        return file_size <= self.max_file_size_for_cache
    
    def generate_file_key(self, file_content: bytes) -> str:
        """Generuj klucz na podstawie hash pliku z wersją"""
        try:
            if not file_content:
                raise ValueError("File content is empty")
            
            hash_val = hashlib.md5(file_content).hexdigest()
            return f"pdf_analysis:{self.cache_version}:{hash_val}"
        except Exception as e:
            logger.error(f"Failed to generate cache key: {e}")
            raise
    
    def set_cache(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Cache wyniku analizy"""
        if not self.is_available():
            return False
            
        try:
            # Dodaj metadane do cache
            cache_data = {
                'data': value,
                'cached_at': datetime.now().isoformat(),
                'version': self.cache_version
            }
            
            serialized = json.dumps(cache_data)
            result = self.client.setex(key, expire, serialized)
            
            if result:
                logger.info(f"Successfully cached result for key: {key}")
            return result
            
        except Exception as e:
            self.metrics['cache_errors'] += 1
            logger.error(f"Redis cache set error for key {key}: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Pobierz z cache"""
        if not self.is_available():
            return None
            
        try:
            cached = self.client.get(key)
            if not cached:
                self.metrics['cache_misses'] += 1
                return None
            
            cache_data = json.loads(cached)
            
            # Sprawdź wersję cache
            if cache_data.get('version') != self.cache_version:
                logger.info(f"Cache version mismatch for key {key}, invalidating")
                self.client.delete(key)
                self.metrics['cache_misses'] += 1
                return None
            
            self.metrics['cache_hits'] += 1
            logger.info(f"Cache hit for key: {key}")
            return cache_data['data']
            
        except Exception as e:
            self.metrics['cache_errors'] += 1
            logger.error(f"Redis cache get error for key {key}: {e}")
            return None
    
    def invalidate_cache(self, pattern: str = None) -> int:
        """Usuń cache według wzorca lub wszystkie"""
        if not self.is_available():
            return 0
            
        try:
            if pattern:
                keys = self.client.keys(pattern)
            else:
                keys = self.client.keys(f"pdf_analysis:{self.cache_version}:*")
            
            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Invalidated {deleted} cache entries")
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Pobierz metryki cache"""
        total_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
        hit_rate = (self.metrics['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.metrics,
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests,
            'redis_available': self.is_available()
        }
    
    def cleanup_old_cache(self, max_age_hours: int = 24) -> int:
        """Usuń stare wpisy cache (opcjonalne maintenance)"""
        if not self.is_available():
            return 0
            
        try:
            # To jest prosty cleanup - w produkcji można użyć Redis TTL
            pattern = f"pdf_analysis:*"
            keys = self.client.keys(pattern)
            deleted = 0
            
            for key in keys:
                try:
                    cached = self.client.get(key)
                    if cached:
                        cache_data = json.loads(cached)
                        cached_at = datetime.fromisoformat(cache_data.get('cached_at', ''))
                        age_hours = (datetime.now() - cached_at).total_seconds() / 3600
                        
                        if age_hours > max_age_hours:
                            self.client.delete(key)
                            deleted += 1
                except Exception:
                    # Jeśli nie można sparsować, usuń
                    self.client.delete(key)
                    deleted += 1
            
            logger.info(f"Cleaned up {deleted} old cache entries")
            return deleted
            
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            return 0

# Singleton instance
redis_client = RedisClient()