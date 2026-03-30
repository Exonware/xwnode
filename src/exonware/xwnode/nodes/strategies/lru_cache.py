"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/lru_cache.py
LRU Cache Strategy Implementation
Least Recently Used (LRU) cache with O(1) get, put, and delete operations.
Uses xwsystem's optimized cache (PylruCache when pylru installed, else FunctoolsLRUCache) for maximum performance.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.20
Generation Date: 27-Oct-2025
"""

from typing import Any
from .base import ACachedStrategy, AKeyValueStrategy
from ...defs import NodeMode


class LRUCacheStrategy(ACachedStrategy, AKeyValueStrategy):
    """
    LRU Cache Strategy - O(1) get/put with automatic eviction
    Implements Least Recently Used eviction policy using xwsystem's optimized cache:
    - O(1) get operation (via xwsystem create_cache: PylruCache when pylru installed)
    - O(1) put operation
    - O(1) delete operation
    - Thread-safe operations (built into xwsystem cache)
    - Automatic eviction when max_size is reached
    - Built-in statistics tracking
    Performance Optimization:
    - Uses xwsystem's create_cache() which defaults to PylruCache when pylru installed (benchmark: ~2.5-3M mixed ops/s)
    - Automatically uses cachebox (Rust-based) if available (even faster)
    - 10-50x faster than manual OrderedDict implementations
    - Leverages ACachedStrategy for consistent cache API
    Use cases:
    - Query result caching
    - Frequently accessed data
    - Fixed-size caches
    - Performance optimization
    Priority alignment:
    - Performance (#4): O(1) operations, leverages xwsystem optimizations
    - Usability (#2): Simple cache interface, consistent with ecosystem
    - Security (#1): Thread-safe by default (via xwsystem cache)
    - Maintainability (#3): Less code, leverages proven xwsystem implementation
    """

    def __init__(self, mode=None, traits=None, max_size: int = 1000, **kwargs):
        """
        Initialize LRU cache using xwsystem optimized cache.
        Args:
            mode: NodeMode for this strategy (passed to base)
            traits: NodeTrait for this strategy (passed to base)
            max_size: Maximum number of entries in cache
            **kwargs: Additional arguments (may contain max_size if passed by flyweight)
        """
        from ...defs import NodeMode, NodeTrait
        # Extract max_size from kwargs if passed by flyweight
        max_size = kwargs.pop('max_size', max_size)
        # Initialize ACachedStrategy which sets up xwsystem cache
        # ACachedStrategy uses create_cache() which provides optimized LRU implementation
        ACachedStrategy.__init__(
            self,
            mode=mode or NodeMode.LRU_CACHE,
            traits=traits or NodeTrait.NONE,
            max_size=max_size,
            cache_name='lru_cache_strategy',
            **kwargs
        )
    # Override get to maintain backward compatibility with facade calls
    # Facade calls: strategy.get(path) - expects None on miss
    # Facade also calls: strategy.get(path, default) - expects default on miss

    def get(self, key: str, default: Any = None) -> Any | None:
        """
        Get value from cache (O(1)).
        Uses xwsystem's optimized cache which automatically handles LRU ordering.
        Args:
            key: Cache key
            default: Default value if not found (optional)
        Returns:
            Cached value or default if not found (None if default not provided)
        """
        # Use ACachedStrategy's get() which uses xwsystem optimized cache
        # Pass default parameter through - ACachedStrategy handles it correctly
        return ACachedStrategy.get(self, key, default=default)
    # put(), delete(), clear(), exists(), get_stats() are inherited from ACachedStrategy
    # They use xwsystem cache which is already optimized

    def get_size(self) -> int:
        """Get current number of entries"""
        return len(self)

    def get_max_size(self) -> int:
        """Get maximum cache size"""
        return self._max_size
    # ANodeStrategy interface implementation

    def get_mode(self) -> NodeMode:
        """Get the node mode for this strategy"""
        return NodeMode.LRU_CACHE

    def supports_operation(self, operation: str) -> bool:
        """Check if operation is supported"""
        supported = {'get', 'put', 'delete', 'exists', 'clear', 'size', 'stats'}
        return operation in supported

    def get_complexity(self, operation: str) -> str:
        """Get time complexity for operation"""
        return "O(1)"  # All operations are O(1)
    # Methods inherited from ACachedStrategy:
    # - has() - uses exists()
    # - keys() - iterator over cache keys
    # - values() - iterator over cache values
    # - items() - iterator over key-value pairs
    # - __len__() - returns cache size
    # - to_native() - converts to dict
    # Additional compatibility methods

    def clear_stats(self) -> None:
        """
        Clear statistics (compatibility method).
        Note: xwsystem cache manages its own statistics. This method is kept
        for backward compatibility but may not clear xwsystem's internal stats.
        """
        # xwsystem cache statistics are managed internally
        # We can't clear them without access to internal cache
        # This is a limitation when using xwsystem cache
        pass
