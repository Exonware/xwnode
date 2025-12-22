"""
#exonware/xwnode/src/exonware/xwnode/common/caching/contracts.py

Cache adapter interface and contracts.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: November 4, 2025
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CacheStats:
    """Statistics for cache performance."""
    
    hits: int = 0
    misses: int = 0
    size: int = 0
    max_size: int = 0
    evictions: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def total_requests(self) -> int:
        """Total cache requests."""
        return self.hits + self.misses
    
    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'size': self.size,
            'max_size': self.max_size,
            'evictions': self.evictions,
            'hit_rate': self.hit_rate,
            'total_requests': self.total_requests
        }


class ICacheAdapter(ABC):
    """
    Adapter interface for cache implementations.
    
    Provides a unified interface for different cache strategies,
    wrapping xwsystem.caching implementations.
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        pass
    
    @abstractmethod
    def put(self, key: str, value: Any) -> None:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cached entries."""
        pass
    
    @abstractmethod
    def get_stats(self) -> CacheStats:
        """
        Get cache statistics.
        
        Returns:
            CacheStats object with performance metrics
        """
        pass
    
    @abstractmethod
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Pattern to match (e.g., "user:*")
            
        Returns:
            Number of entries invalidated
        """
        pass
    
    def contains(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
        """
        return self.get(key) is not None
    
    def get_many(self, keys: list[str]) -> dict[str, Any]:
        """
        Get multiple values from cache.
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary of key-value pairs for found entries
        """
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    def put_many(self, items: dict[str, Any]) -> None:
        """
        Store multiple values in cache.
        
        Args:
            items: Dictionary of key-value pairs to cache
        """
        for key, value in items.items():
            self.put(key, value)


class ICacheFactory(ABC):
    """Factory interface for creating cache adapters."""
    
    @abstractmethod
    def create_cache(
        self,
        component: str,
        size: int,
        **options
    ) -> ICacheAdapter:
        """
        Create a cache adapter instance.
        
        Args:
            component: Component name (e.g., "graph", "traversal")
            size: Maximum cache size
            **options: Additional cache-specific options
            
        Returns:
            Cache adapter instance
        """
        pass

