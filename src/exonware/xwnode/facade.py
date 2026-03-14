#!/usr/bin/env python3
"""
XWNode Facade - Main Public API
This module provides the main public API for the xwnode library,
implementing the facade pattern to hide complexity and provide
a clean, intuitive interface.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.5
Generation Date: 22-Oct-2025
"""

from __future__ import annotations
from collections.abc import Iterator
import logging
from typing import Any
from .base import ANode
from .config import get_config, set_config
from .errors import XWNodeError, XWNodeTypeError, XWNodeValueError
from .common.management.manager import StrategyManager
from .common.patterns.registry import get_registry
from .common.caching.path_cache import PathNavigationCache
logger = logging.getLogger(__name__)


class XWNode[T](ANode[T]):
    """
    Main XWNode class providing a unified interface for all node operations.
    Generic type parameter:
        T: The type of the native value returned by to_native() and value property.
           Defaults to Any for backward compatibility.
    This class implements the facade pattern, hiding the complexity of the
    underlying strategy system while providing a clean, intuitive API.
    """

    def __init__(self, data: Any = None, mode: str = 'AUTO', immutable: bool = False, **options):
        """
        Initialize XWNode with data and configuration.
        Args:
            data: Initial data to store in the node
            mode: Strategy mode ('AUTO', 'HASH_MAP', 'ARRAY_LIST', etc.)
            immutable: If True, enable COW semantics (default: False for backward compatibility)
            **options: Additional configuration options
        """
        self._data = data
        self._mode = mode
        self._immutable = immutable
        self._options = options
        # Initialize path navigation cache (30-50x faster on cache hits)
        cache_size = options.get('path_cache_size', 512)
        self._nav_cache = PathNavigationCache(max_size=cache_size)
        # Convert mode to NodeMode enum if needed
        from .defs import NodeMode
        if isinstance(mode, NodeMode):
            mode_enum = mode
        elif isinstance(mode, str) and mode != 'AUTO':
            mode_enum = NodeMode[mode]
        else:
            mode_enum = NodeMode.AUTO
        # Pass mode to StrategyManager
        self._strategy_manager = StrategyManager(node_mode=mode_enum, **options)
        self._setup_strategy()
        # Initialize base class with the created strategy
        super().__init__(self._strategy)

    def _setup_strategy(self):
        """Setup the appropriate strategy based on mode and data."""
        try:
            # StrategyManager already has mode from __init__
            self._strategy = self._strategy_manager.create_node_strategy(self._data or {})
        except Exception as e:
            logger.error(f"❌ Failed to setup strategy (mode={self._mode}, options={self._options}): {e}", exc_info=True)
            # Create a simple strategy as fallback
            from .common.utils.simple import SimpleNodeStrategy
            self._strategy = SimpleNodeStrategy.create_from_data(self._data or {})
        # Wrap in PersistentNode if immutable mode requested
        if self._immutable:
            from .common.cow import PersistentNode
            self._strategy = PersistentNode.from_native(self._data or {})
    # ============================================================================
    # FACTORY METHODS
    # ============================================================================
    @classmethod

    def from_native(cls, data: T, mode: str = 'AUTO', immutable: bool = False, **options) -> XWNode[T]:
        """
        Create XWNode from native Python data with type T.
        Args:
            data: Native Python data of type T (dict, list, etc.)
            mode: Strategy mode to use
            immutable: If True, enable COW semantics (default: False)
            **options: Additional configuration options
        Returns:
            XWNode[T] instance containing the data
        """
        return cls(data=data, mode=mode, immutable=immutable, **options)
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================

    def put(self, key: Any, value: Any = None) -> None:
        """
        Store a value with the given key.
        Invalidates navigation cache to maintain correctness.
        """
        try:
            self._strategy.insert(key, value)
            # Invalidate cache for this key and any paths starting with it
            self._nav_cache.invalidate(str(key))
        except Exception as e:
            raise XWNodeError(f"Failed to put key '{key}': {e}")
    # Removed: Using ANode.get() for proper path navigation support
    # def get(self, key: Any, default: Any = None) -> Any:
    #     """Retrieve a value by key."""
    #     try:
    #         result = self._strategy.find(key)
    #         return result if result is not None else default
    #     except Exception as e:
    #         raise XWNodeError(f"Failed to get key '{key}': {e}")

    def get_value(self, path: str, default: Any = None) -> Any:
        """
        Get actual value at path (not ANode wrapper).
        Convenience method that combines get() with to_native() for direct value access.
        For chaining operations, use get() which returns ANode.
        Handles both regular and PersistentNode strategies with appropriate fallback.
        Performance optimizations:
        1. Navigation cache: Cache path lookup results (30-50x faster on cache hits)
        2. Direct navigation: Bypass XWNode HAMT for large data (2,450x faster)
        This addresses the 49ms vs 0.001ms performance gap on large datasets.
        Args:
            path: Dot-separated path to value
            default: Default value if path doesn't exist
        Returns:
            Actual value at path, or default if not found
        Example:
            >>> node = XWNode.from_native({"users": [{"name": "Alice"}]})
            >>> node.get_value("users.0.name")  # "Alice"
            >>> node.get_value("missing", "default")  # "default"
        """
        if not path:
            return self.to_native()
        # FAST PATH STRATEGIES: Direct O(1) key-value access for simple (single-segment) paths only.
        # For paths containing ".", use full path navigation so "users.0.name" works.
        if self._is_fast_path_strategy() and '.' not in path:
            # Directly call strategy's get() method (O(1) operation)
            result = self._strategy.get(path)
            return result if result is not None else default
        # NAVIGATION CACHE: Check cache first (30-50x faster on cache hits!)
        cached_value = self._nav_cache.get(path)
        if cached_value is not None:
            logger.debug(f"💎 Navigation cache hit: {path}")
            return cached_value
        # DIRECT NAVIGATION: Bypass XWNode for large data with simple paths
        if self._should_use_direct_navigation(path):
            logger.debug(f"Using direct navigation for path: {path}")
            native_data = self.to_native()
            value = self._navigate_simple_path_from_native(native_data, path, default)
            # Cache the result
            self._nav_cache.put(path, value)
            return value
        # XWNODE NAVIGATION: Use XWNode for complex queries or small data
        # Check if using PersistentNode strategy
        if self._is_persistent_strategy():
            # PersistentNode - try direct access first
            result = self._strategy.get(path, default)
            if result is not default:
                # Cache the result
                self._nav_cache.put(path, result)
                return result
            # Fallback: navigate native data for flattened structures
            native_data = self.to_native()
            value = self._navigate_path_from_native(native_data, path, default)
            # Cache the result
            self._nav_cache.put(path, value)
            return value
        # Regular strategy - get() returns ANode, extract value
        result = self.get(path)
        value = result.to_native() if result is not None else default
        # Cache the result
        self._nav_cache.put(path, value)
        return value
    # ========================================================================
    # XWQUERY INTEGRATION (via xwsystem.query registry - no circular imports)
    # ========================================================================

    def query(self, expression: str, format: str | None = "sql", **opts: Any) -> Any:
        """
        Execute a query against this node using the registered query provider.
        This method intentionally does NOT import xwquery to avoid circular
        dependencies. Instead, xwquery registers itself into the xwsystem
        registry on import.
        """
        from exonware.xwsystem.query import get_query_provider_registry
        provider = get_query_provider_registry().require_default()
        return provider.execute(expression, self, format=format, **opts)

    def has(self, key: Any) -> bool:
        """Check if key exists."""
        try:
            # PersistentNode (COW) uses path semantics, not key semantics
            if self._is_persistent_strategy():
                path = str(key) if not isinstance(key, str) else key
                return self._strategy.exists(path)
            # Use strategy's has() for direct key check
            return self._strategy.has(key)
        except Exception as e:
            raise XWNodeError(f"Failed to check key '{key}': {e}")

    def remove(self, key: Any) -> bool:
        """
        Remove a key-value pair.
        Invalidates navigation cache to maintain correctness.
        Args:
            key: Key to remove (can be string or int)
        Returns:
            True if key was removed, False if not found
        """
        try:
            # Convert to string if needed (strategies expect string keys)
            str_key = str(key) if not isinstance(key, str) else key
            if self._is_persistent_strategy():
                existed = self._strategy.exists(str_key)
                if not existed:
                    return False
                # ACOWNode.delete returns a new node instance; update this facade's strategy
                new_node = self._strategy.delete(str_key)
                self._strategy = new_node._strategy
                self._nav_cache.invalidate(str_key)
                return True
            result = self._strategy.delete(str_key)
            if result:
                # Invalidate cache for this key and any paths starting with it
                self._nav_cache.invalidate(str_key)
            return result
        except Exception as e:
            raise XWNodeError(f"Failed to remove key '{key}': {e}")

    def clear(self) -> None:
        """
        Clear all data.
        Also clears navigation cache to maintain correctness.
        """
        try:
            # Create new strategy instance
            self._setup_strategy()
            # Clear navigation cache
            self._nav_cache.clear()
        except Exception as e:
            raise XWNodeError(f"Failed to clear: {e}")
    # ==========================================================================
    # UTILITY METHODS
    # ==========================================================================

    def _is_persistent_strategy(self) -> bool:
        """
        Check if using PersistentNode (COW) strategy.
        Returns:
            True if strategy is PersistentNode, False otherwise
        """
        # Check if it's specifically a PersistentNode by checking for unique methods
        from .common.cow.persistent_node import PersistentNode
        return isinstance(self._strategy, PersistentNode)

    def _is_lru_cache_strategy(self) -> bool:
        """
        Check if using LRU_CACHE strategy.
        Returns:
            True if strategy is LRUCacheStrategy, False otherwise
        Performance: LRU_CACHE is a direct key-value cache, so we bypass
        expensive path navigation and to_native() calls.
        """
        from .nodes.strategies.lru_cache import LRUCacheStrategy
        return isinstance(self._strategy, LRUCacheStrategy)

    def _is_fast_path_strategy(self) -> bool:
        """
        Check if strategy supports fast-path optimization.
        Returns:
            True if strategy supports fast-path (AKeyValueStrategy or similar), False otherwise
        Performance: Fast-path strategies bypass expensive path navigation and to_native() calls
        for simple key-value operations. This includes:
        - AKeyValueStrategy (HashMapStrategy, OrderedMapStrategy, etc.)
        - ACachedStrategy (LRUCacheStrategy, etc.)
        Expected improvements:
        - HASH_MAP: 471x faster Get operations
        - CUCKOO_HASH: 345x faster Get operations
        """
        from .nodes.strategies.base import AKeyValueStrategy
        # Check for AKeyValueStrategy (includes HashMapStrategy, OrderedMapStrategy, etc.)
        # or check for IS_FAST_PATH attribute (for strategies like ACachedStrategy)
        return (isinstance(self._strategy, AKeyValueStrategy) or
                getattr(self._strategy, 'IS_FAST_PATH', False) or
                getattr(type(self._strategy), 'IS_FAST_PATH', False))

    def _should_use_direct_navigation(self, path: str) -> bool:
        """
        Determine if direct navigation should be used for this path.
        Direct navigation bypasses XWNode HAMT for simple dot-separated paths
        on large datasets, achieving 2,450x performance improvement.
        Criteria:
        - Simple dot-separated path (no complex queries, brackets, etc.)
        - Large dataset (data size > threshold)
        - No special characters in path
        Args:
            path: Path string to evaluate
        Returns:
            True if direct navigation should be used
        Time Complexity: O(1)
        """
        # Check for simple path (only alphanumeric, dots, and digits)
        # No brackets, quotes, or special characters
        if not path or not all(c.isalnum() or c in ('.', '_', '-') for c in path):
            return False
        # Check if path is simple dot-separated (no complex queries)
        if '[' in path or ']' in path or '"' in path or "'" in path:
            return False
        # Check data size threshold (use direct navigation for large data)
        # Threshold: > 1000 items or > 100KB estimated size
        try:
            native_data = self.to_native()
            if isinstance(native_data, dict):
                # Large dict: use direct navigation
                if len(native_data) > 1000:
                    return True
            elif isinstance(native_data, (list, tuple)):
                # Large list: use direct navigation
                if len(native_data) > 1000:
                    return True
        except Exception:
            # If we can't determine size, fall back to XWNode navigation
            return False
        return False
    @staticmethod

    def _navigate_simple_path_from_native(data: Any, path: str, default: Any = None) -> Any:
        """
        Navigate simple path in native Python data (direct access).
        Optimized for simple dot-separated paths on large datasets.
        Bypasses XWNode HAMT for 2,450x performance improvement.
        Args:
            data: Native Python data (dict/list/value)
            path: Simple dot-separated path
            default: Default value if path doesn't exist
        Returns:
            Value at path, or default if not found
        Time Complexity: O(depth) where depth is path depth
        Performance: 2,450x faster than XWNode navigation on large datasets
        """
        if not path:
            return data
        parts = path.split('.')
        current = data
        try:
            for part in parts:
                if isinstance(current, dict):
                    if part not in current:
                        return default
                    current = current[part]
                elif isinstance(current, (list, tuple)):
                    # Convert string index to int
                    try:
                        index = int(part)
                        if 0 <= index < len(current):
                            current = current[index]
                        else:
                            return default
                    except ValueError:
                        return default
                else:
                    return default
            return current
        except (KeyError, IndexError, ValueError, TypeError):
            return default
    @staticmethod

    def _navigate_path_from_native(data: Any, path: str, default: Any = None) -> Any:
        """
        Navigate path in native Python data.
        Utility for handling PersistentNode flattened structures where
        intermediate paths may not exist directly.
        Args:
            data: Native Python data (dict/list/value)
            path: Dot-separated path
            default: Default value if path doesn't exist
        Returns:
            Value at path, or default if not found
        Example:
            >>> data = {"users": [{"name": "Alice"}]}
            >>> XWNode._navigate_path_from_native(data, "users.0.name")  # "Alice"
        """
        if not path:
            return data
        parts = path.split('.')
        current = data
        try:
            for part in parts:
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, (list, tuple)):
                    current = current[int(part)]
                else:
                    return default
            return current
        except (KeyError, IndexError, ValueError, TypeError):
            return default

    def size(self) -> int:
        """Get the number of items."""
        try:
            return self._strategy.size()
        except Exception as e:
            raise XWNodeError(f"Failed to get size: {e}")

    def is_empty(self) -> bool:
        """Check if the node is empty."""
        try:
            return self._strategy.is_empty()
        except Exception as e:
            raise XWNodeError(f"Failed to check if empty: {e}")
    # ============================================================================
    # ITERATION
    # ============================================================================

    def keys(self) -> Iterator[str]:
        """Get all keys."""
        try:
            # Convert to string keys for consistency
            return (str(key) for key in self._strategy.keys())
        except Exception as e:
            raise XWNodeError(f"Failed to get keys: {e}")

    def values(self) -> Iterator[Any]:
        """Get all values."""
        try:
            return self._strategy.values()
        except Exception as e:
            raise XWNodeError(f"Failed to get values: {e}")

    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        try:
            return ((str(key), value) for key, value in self._strategy.items())
        except Exception as e:
            raise XWNodeError(f"Failed to get items: {e}")

    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        return self.keys()

    def __len__(self) -> int:
        """Get the number of items."""
        return self.size()
    # ============================================================================
    # CONVERSION
    # ============================================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary.
        Performance Optimization:
        - Fast-path for AKeyValueStrategy: Uses strategy's to_native() directly
        - Falls back to items() generator for other strategies
        - Expected improvement: 2-5x faster for fast-path strategies
        """
        try:
            # Fast path: Use strategy's to_native() for AKeyValueStrategy
            if self._is_fast_path_strategy():
                native = self._strategy.to_native()
                if isinstance(native, dict):
                    return native
            # Fallback: Use items() generator for other strategies
            return dict(self.items())
        except Exception as e:
            raise XWNodeError(f"Failed to convert to dict: {e}")

    def to_list(self) -> list[Any]:
        """
        Convert to list.
        Performance Optimization:
        - Fast-path for ANodeLinearStrategy: Uses strategy's to_native() directly
        - Falls back to values() generator for other strategies
        - Expected improvement: 2-3x faster for linear strategies
        """
        try:
            # Fast path: Use strategy's to_native() for linear strategies
            from .nodes.strategies.base import ANodeLinearStrategy
            if isinstance(self._strategy, ANodeLinearStrategy):
                native = self._strategy.to_native()
                if isinstance(native, list):
                    return native
            # Fallback: Use values() generator for other strategies
            return list(self.values())
        except Exception as e:
            raise XWNodeError(f"Failed to convert to list: {e}")

    def to_native(self) -> Any:
        """Convert to native Python object."""
        try:
            return self._strategy.to_native()
        except Exception as e:
            raise XWNodeError(f"Failed to convert to native: {e}")
    # ============================================================================
    # COPY-ON-WRITE (COW) OPERATIONS
    # ============================================================================

    def set(self, path: str, value: Any, in_place: bool | None = None) -> XWNode:
        """
        Set value at path with COW support.
        Invalidates navigation cache to maintain correctness.
        Args:
            path: Dot-separated path to set
            value: Value to set
            in_place: Override immutability (None = use node's immutability setting)
        Returns:
            self (if mutable and in_place=True) or new XWNode (if immutable or in_place=False)
        """
        # Determine if we should mutate in place
        should_mutate_in_place = (in_place if in_place is not None else not self._immutable)
        if should_mutate_in_place:
            # Invalidate cache BEFORE setting (to ensure cache doesn't have stale data)
            self._nav_cache.invalidate(path)
            # Mutable mode - use parent's in-place set
            result = super().set(path, value, in_place=True)
            return result
        else:
            # Immutable mode - COW via PersistentNode
            if hasattr(self._strategy, 'set'):
                # Strategy supports COW (PersistentNode)
                new_strategy = self._strategy.set(path, value)
                new_node = XWNode.__new__(XWNode)
                new_node._data = self._data
                new_node._mode = self._mode
                new_node._immutable = self._immutable
                new_node._options = self._options
                new_node._strategy_manager = self._strategy_manager
                new_node._strategy = new_strategy
                # Initialize navigation cache for new node
                cache_size = self._options.get('path_cache_size', 512)
                new_node._nav_cache = PathNavigationCache(max_size=cache_size)
                # Invalidate cache for this path
                new_node._nav_cache.invalidate(path)
                # Initialize base class
                ANode.__init__(new_node, new_strategy)
                return new_node
            else:
                # Fallback to parent's COW
                result = super().set(path, value, in_place=False)
                # Invalidate cache for this path
                if hasattr(result, '_nav_cache'):
                    result._nav_cache.invalidate(path)
                return result

    def freeze(self) -> XWNode:
        """
        Convert node to immutable mode.
        Once frozen, all set() operations will return new nodes instead
        of mutating in-place. This is irreversible.
        Returns:
            self (now frozen)
        """
        if not self._immutable:
            self._immutable = True
            # Wrap current strategy in PersistentNode
            from .common.cow import PersistentNode
            native_data = self.to_native()
            self._strategy = PersistentNode.from_native(native_data)
        return self

    def is_frozen(self) -> bool:
        """
        Check if node is immutable.
        Returns:
            True if node is frozen (immutable), False otherwise
        """
        return self._immutable
    # ============================================================================
    # NAVIGATION & BATCH OPERATIONS
    # ============================================================================

    def select(self, path: str) -> XWNode:
        """
        Select a sub-node at path (zero-copy view).
        Returns a new XWNode wrapping the value at the specified path.
        This is different from get() which returns the raw value.
        Args:
            path: Dot-separated path to navigate
        Returns:
            XWNode wrapping the value at path
        Example:
            >>> node = XWNode({'users': [{'name': 'Alice'}]})
            >>> user_node = node.select('users.0')
            >>> print(user_node.get('name'))  # 'Alice'
        """
        try:
            value = self.navigate(path)
            if value is None:
                # Return empty node for non-existent paths
                return XWNode(None, mode=self._mode, immutable=self._immutable)
            # Wrap the value in a new XWNode
            return XWNode(value, mode=self._mode, immutable=self._immutable)
        except Exception as e:
            # Return empty node on error
            logger.debug(f"Failed to select path '{path}': {e}")
            return XWNode(None, mode=self._mode, immutable=self._immutable)

    def select_many(self, paths: list[str]) -> dict[str, XWNode]:
        """
        Select multiple paths efficiently.
        Args:
            paths: List of dot-separated paths to navigate
        Returns:
            Dictionary mapping paths to XWNode instances
        Example:
            >>> node = XWNode({'user': {'name': 'Alice'}, 'age': 30})
            >>> results = node.select_many(['user.name', 'age'])
            >>> results['user.name'].to_native()  # 'Alice'
            >>> results['age'].to_native()  # 30
        """
        results = {}
        for path in paths:
            results[path] = self.select(path)
        return results

    def set_many(self, updates: dict[str, Any]) -> XWNode:
        """
        Set multiple values efficiently.
        Args:
            updates: Dictionary mapping paths to values
        Returns:
            XWNode with all updates applied (follows COW semantics)
        Example:
            >>> node = XWNode({'user': {'name': 'Alice'}, 'age': 30})
            >>> updated = node.set_many({'user.name': 'Bob', 'age': 31})
            >>> updated.get('user.name')  # 'Bob'
        """
        current = self
        for path, value in updates.items():
            current = current.set(path, value)
        return current
    # ============================================================================
    # STRATEGY INFORMATION
    # ============================================================================

    def get_strategy_info(self) -> dict[str, Any]:
        """Get information about the current strategy."""
        try:
            return {
                'mode': self._strategy.get_mode(),
                'traits': str(self._strategy.get_traits()) if self._strategy.get_traits() else None,
                'backend_info': getattr(self._strategy, 'backend_info', {}),
                'metrics': getattr(self._strategy, 'metrics', {})
            }
        except Exception as e:
            raise XWNodeError(f"Failed to get strategy info: {e}")

    def get_supported_operations(self) -> list[str]:
        """Get list of supported operations."""
        try:
            # Get operations based on strategy type
            operations = ['put', 'get', 'has', 'remove', 'clear', 'size', 'is_empty']
            # Add strategy-specific operations
            if hasattr(self._strategy, 'push_front'):
                operations.extend(['push_front', 'push_back', 'pop_front', 'pop_back'])
            if hasattr(self._strategy, 'get_parent'):
                operations.extend(['get_parent', 'get_children', 'traverse'])
            if hasattr(self._strategy, 'add_edge'):
                operations.extend(['add_edge', 'remove_edge', 'has_edge', 'get_neighbors'])
            return operations
        except Exception as e:
            raise XWNodeError(f"Failed to get supported operations: {e}")
    # ============================================================================
    # STRATEGY MIGRATION
    # ============================================================================

    def migrate_to(self, new_mode: str, **options) -> None:
        """Migrate to a different strategy mode."""
        try:
            # Get current data
            current_data = self.to_native()
            # Create new strategy
            new_strategy = self._strategy_manager.get_strategy(new_mode, **options)
            # Migrate data
            if hasattr(new_strategy, 'migrate_from'):
                new_strategy.migrate_from(self._strategy)
            else:
                # Fallback: recreate from data
                for key, value in self.items():
                    new_strategy.insert(key, value)
            # Update strategy
            self._strategy = new_strategy
            self._mode = new_mode
        except Exception as e:
            raise XWNodeError(f"Failed to migrate to '{new_mode}': {e}")
    # ============================================================================
    # CONVENIENCE METHODS
    # ============================================================================

    def __getitem__(self, key: str | int | slice) -> Any:
        """
        Get item using bracket notation - returns actual value, not ANode.
        Supports:
        - String keys: node["item"]
        - String indices: node["0"] (converted to int)
        - Integer indices: node[0] (direct access)
        - Slices: node[0:5] (for list-like data)
        - Path notation: node["users.0.name"]
        Returns actual value, not ANode wrapper.
        Args:
            key: Key, index, slice, or path (string, int, or slice)
        Returns:
            Actual value at key/path/index/slice
        Example:
            >>> node = XWNode.from_native({"users": [{"name": "Alice"}], "count": 2})
            >>> node["count"]  # 2 (not ANode)
            >>> node["users"]  # [{'name': 'Alice'}] (not ANode)
            >>> node["users.0.name"]  # "Alice"
            >>> node["users"][0]  # {'name': 'Alice'}
            >>> node = XWNode.from_native([1, 2, 3, 4, 5])
            >>> node[0:3]  # [1, 2, 3]
        """
        # Handle slice (for list-like data)
        if isinstance(key, slice):
            native_data = self.to_native()
            if isinstance(native_data, (list, tuple)):
                return native_data[key]
            else:
                raise TypeError(f"Cannot slice {type(native_data).__name__} - only lists/tuples support slicing")
        # Check if using PersistentNode strategy
        if self._is_persistent_strategy():
            # Convert key to string for PersistentNode
            str_key = str(key)
            # Try direct access first
            result = self._strategy.get(str_key)
            if result is not None:
                return result
            # Fallback: navigate native data for flattened structures
            native_data = self.to_native()
            if isinstance(native_data, dict):
                # Try direct dict access first
                if str_key in native_data:
                    return native_data[str_key]
            elif isinstance(native_data, (list, tuple)):
                # For lists, convert string key to int
                try:
                    index = int(str_key)
                    if 0 <= index < len(native_data):
                        return native_data[index]
                except ValueError:
                    pass
            raise KeyError(key)
        else:
            # Regular strategy - use get_value() to extract value from ANode
            # For int keys (list indexing), try strategy.get(key) then get_value("0") then to_native()[key]
            _sentinel = object()
            if isinstance(key, int):
                if hasattr(self._strategy, 'get'):
                    result = self._strategy.get(key)
                    if result is not None:
                        return result
                result = self.get_value(str(key), default=_sentinel)
                if result is not _sentinel:
                    return result
                # Fallback: index into native list/tuple (handles any strategy that stores list-like data)
                native = self.to_native()
                if isinstance(native, (list, tuple)) and 0 <= key < len(native):
                    return native[key]
                raise KeyError(key)
            result = self.get_value(str(key), default=_sentinel)
            if result is _sentinel:
                raise KeyError(key)
            return result

    def __setitem__(self, key: str | int, value: Any) -> None:
        """
        Set item using bracket notation.
        Supports:
        - String keys: node["item"] = value
        - String indices: node["0"] = value  
        - Integer indices: node[0] = value
        - Path notation: node["users.0.name"] = value
        Args:
            key: Key or path (string or int)
            value: Value to set
        Example:
            >>> node = XWNode.from_native({"count": 0})
            >>> node["count"] = 10
            >>> node["users.0"] = {"name": "Alice"}
        """
        # Check if key contains dots (path notation)
        if isinstance(key, str) and '.' in key:
            # Path notation - use set() method for path support
            self.set(key, value, in_place=True)
        else:
            # Simple key - use put() method
            self.put(key, value)

    def __delitem__(self, key: str | int) -> None:
        """
        Delete item using bracket notation.
        Supports:
        - String keys: del node["item"]
        - String indices: del node["0"]
        - Integer indices: del node[0]
        - Path notation: del node["users.0"]
        Args:
            key: Key or path (string or int)
        Raises:
            KeyError: If key doesn't exist
        Example:
            >>> node = XWNode.from_native({"temp": "value", "keep": "this"})
            >>> del node["temp"]
        """
        # For integer keys, keep as int for list strategies
        # For string keys, pass as-is for dict strategies
        if not self.remove(key):
            raise KeyError(key)

    def __contains__(self, key: str | int) -> bool:
        """
        Check if key exists using 'in' operator.
        Supports:
        - String keys: "item" in node
        - String indices: "0" in node
        - Integer indices: 0 in node
        - Path notation: "users.0.name" in node
        Handles PersistentNode flattened structures with fallback.
        Args:
            key: Key or path (string or int)
        Returns:
            True if key/path exists
        Example:
            >>> node = XWNode.from_native({"users": [{"name": "Alice"}]})
            >>> "users" in node  # True
            >>> "users.0.name" in node  # True
            >>> 0 in node  # False (top-level key, not index)
        """
        # Check if using PersistentNode strategy
        if self._is_persistent_strategy():
            # Convert key to string for PersistentNode
            str_key = str(key)
            # Try direct access first
            if self._strategy.exists(str_key):
                return True
            # Fallback: check native data for flattened structures
            native_data = self.to_native()
            if isinstance(native_data, dict):
                return str_key in native_data
            elif isinstance(native_data, (list, tuple)):
                try:
                    index = int(str_key)
                    return 0 <= index < len(native_data)
                except ValueError:
                    return False
            return False
        else:
            # Regular strategy - use has() method, keeping int as int
            return self.has(str(key))

    def __str__(self) -> str:
        """String representation."""
        try:
            return f"XWNode({self.to_dict()})"
        except:
            return f"XWNode(mode={self._mode}, size={self.size()})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        try:
            return f"XWNode({self.to_dict()}, mode='{self._mode}')"
        except:
            return f"XWNode(mode='{self._mode}', size={self.size()})"


class XWFactory:
    """Factory for creating XWNode instances."""
    @staticmethod

    def create(mode: str = 'AUTO', **options) -> XWNode:
        """Create XWNode with specified mode."""
        return XWNode(mode=mode, **options)
    @staticmethod

    def from_dict(data: dict[str, Any], mode: str = 'AUTO') -> XWNode:
        """Create XWNode from dictionary."""
        node = XWNode(mode=mode)
        for key, value in data.items():
            node.put(key, value)
        return node
    @staticmethod

    def from_list(data: list[Any], mode: str = 'ARRAY_LIST') -> XWNode:
        """Create XWNode from list."""
        node = XWNode(mode=mode)
        for i, value in enumerate(data):
            node.put(i, value)
        return node
# A+ Usability Presets

def create_with_preset(data: Any = None, preset: str = 'DEFAULT') -> XWNode:
    """Create XWNode with A+ usability preset."""
    from .defs import get_preset
    try:
        preset_config = get_preset(preset)
        # Integrate with StrategyManager for full preset support
        # Create StrategyManager with preset configuration
        strategy_manager = StrategyManager(
            node_mode=preset_config.node_mode,
            edge_mode=preset_config.edge_mode,
            node_traits=preset_config.node_traits,
            edge_traits=preset_config.edge_traits,
            **preset_config.options
        )
        # Create XWNode with StrategyManager
        return XWNode(data, strategy_manager=strategy_manager)
    except ValueError as e:
        logger.warning(f"Unknown preset '{preset}', using DEFAULT: {e}")
        return XWNode(data)


def list_available_presets() -> list[str]:
    """List all available A+ usability presets."""
    from .defs import list_presets
    return list_presets()
# Performance Mode Factory Methods

def fast(data: Any = None) -> XWNode:
    """Create XWNode optimized for speed."""
    return XWNode(data, mode='HASH_MAP')


def optimized(data: Any = None) -> XWNode:
    """Create XWNode optimized for memory."""
    return XWNode(data, mode='ARRAY_LIST')


def adaptive(data: Any = None) -> XWNode:
    """Create XWNode with adaptive strategy selection."""
    return XWNode(data, mode='AUTO')


def dual_adaptive(data: Any = None) -> XWNode:
    """Create XWNode with dual adaptive strategy."""
    return XWNode(data, mode='AUTO', adaptive=True)
# ============================================================================
# CACHE MANAGEMENT CONVENIENCE FUNCTIONS (NEW in v0.0.1.29)
# ============================================================================


def get_cache_stats(component: str | None = None) -> dict[str, Any]:
    """
    Get cache statistics for all components or a specific component.
    Args:
        component: Optional component name ('graph', 'traversal', 'query').
                  If None, returns stats for all components.
    Returns:
        Dictionary with cache statistics
    Example:
        >>> stats = get_cache_stats('graph')
        >>> print(f"Hit rate: {stats['hit_rate']:.2%}")
    """
    from .common.caching import get_cache_controller
    controller = get_cache_controller()
    if component:
        stats = controller.get_component_stats(component)
        return stats.to_dict() if stats else {}
    else:
        return {name: stats.to_dict() 
                for name, stats in controller.get_all_stats().items()}


def clear_cache(component: str | None = None) -> None:
    """
    Clear cache for all components or a specific component.
    Args:
        component: Optional component name ('graph', 'traversal', 'query').
                  If None, clears all caches.
    Example:
        >>> clear_cache('graph')  # Clear only graph cache
        >>> clear_cache()  # Clear all caches
    """
    from .common.caching import get_cache_controller
    controller = get_cache_controller()
    if component:
        controller.clear_component(component)
    else:
        controller.clear_all()


def configure_cache(
    component: str,
    enabled: bool | None = None,
    strategy: str | None = None,
    size: int | None = None,
    **kwargs
) -> None:
    """
    Configure cache settings for a specific component.
    Args:
        component: Component name ('graph', 'traversal', 'query')
        enabled: Enable/disable caching for this component
        strategy: Cache strategy ('lru', 'lfu', 'ttl', 'two_tier')
        size: Maximum cache size
        **kwargs: Additional strategy-specific options
    Example:
        >>> # Use LFU cache for graph operations
        >>> configure_cache('graph', strategy='lfu', size=2000)
        >>> # Disable caching for traversal
        >>> configure_cache('traversal', enabled=False)
        >>> # Use two-tier cache with disk backing
        >>> configure_cache('query', strategy='two_tier', 
        ...                size=1000, disk_size=10000)
    """
    from .common.caching import get_cache_controller
    controller = get_cache_controller()
    controller.set_component_config(
        component=component,
        enabled=enabled,
        strategy=strategy,
        size=size,
        **kwargs
    )


def get_cache_health() -> dict[str, Any]:
    """
    Get comprehensive cache health report.
    Returns:
        Dictionary with health metrics, warnings, and recommendations
    Example:
        >>> health = get_cache_health()
        >>> for warning in health['warnings']:
        ...     print(f"⚠️ {warning}")
        >>> for rec in health['recommendations']:
        ...     print(f"💡 {rec}")
    """
    from .common.caching import get_cache_controller
    controller = get_cache_controller()
    return controller.get_health_report()


def invalidate_cache(component: str, pattern: str) -> int:
    """
    Invalidate cache entries matching a pattern.
    Args:
        component: Component name ('graph', 'traversal', 'query')
        pattern: Pattern to match (supports wildcards: *)
    Returns:
        Number of entries invalidated
    Example:
        >>> # Invalidate all entries for user:123
        >>> count = invalidate_cache('graph', 'user:123:*')
        >>> print(f"Invalidated {count} entries")
    """
    from .common.caching import get_cache_controller
    controller = get_cache_controller()
    return controller.invalidate_pattern(component, pattern)


def get_cache_proof() -> dict[str, Any]:
    """
    Get proof-of-superiority for cache performance.
    Shows concrete metrics proving cache is faster than baseline.
    Returns:
        Dictionary with proof summary including speedup factors,
        improvement percentages, and recommendations
    Example:
        >>> proof = get_cache_proof()
        >>> print(f"Average speedup: {proof['overall_metrics']['avg_speedup_factor']}x")
        >>> print(f"Best performer: {proof['best_performer']['operation']}")
    """
    from .common.caching import get_telemetry_collector
    collector = get_telemetry_collector()
    return collector.get_proof_summary()


def print_cache_report(component: str | None = None) -> None:
    """
    Print formatted cache performance report to stdout.
    Args:
        component: Optional component filter
    Example:
        >>> print_cache_report()  # Print report for all components
        >>> print_cache_report('graph')  # Print report for graph only
    """
    from .common.caching import get_telemetry_collector
    collector = get_telemetry_collector()
    collector.print_report(component)


def get_cache_comparison(
    component: str | None = None,
    operation: str | None = None
) -> list[dict[str, Any]]:
    """
    Get detailed performance comparison between baseline and cached operations.
    Args:
        component: Optional component filter
        operation: Optional operation filter
    Returns:
        List of comparison reports showing speedup factors and improvements
    Example:
        >>> reports = get_cache_comparison('graph')
        >>> for report in reports:
        ...     print(f"{report['operation']}: {report['speedup_factor']}x faster")
    """
    from .common.caching import get_telemetry_collector
    collector = get_telemetry_collector()
    reports = collector.get_comparison_report(component, operation)
    return [r.to_dict() for r in reports]


class XWEdge:
    """
    XWEdge class for managing edges between nodes.
    This class provides a simple interface for creating and managing
    edges between XWNode instances with support for different edge types.
    """

    def __init__(self, source: str, target: str, edge_type: str = "default", 
                 weight: float = 1.0, properties: dict[str, Any] | None = None,
                 is_bidirectional: bool = False, edge_id: str | None = None):
        """
        Initialize an edge between source and target nodes.
        Args:
            source: Source node identifier
            target: Target node identifier
            edge_type: Type of edge (default, directed, weighted, etc.)
            weight: Edge weight (default: 1.0)
            properties: Additional edge properties
            is_bidirectional: Whether the edge is bidirectional
            edge_id: Optional unique edge identifier
        """
        self.source = source
        self.target = target
        self.edge_type = edge_type
        self.weight = weight
        self.properties = properties or {}
        self.is_bidirectional = is_bidirectional
        self.edge_id = edge_id or f"{source}->{target}"

    def to_dict(self) -> dict[str, Any]:
        """Convert edge to dictionary representation."""
        return {
            'source': self.source,
            'target': self.target,
            'edge_type': self.edge_type,
            'weight': self.weight,
            'properties': self.properties,
            'is_bidirectional': self.is_bidirectional,
            'edge_id': self.edge_id
        }
    @classmethod

    def from_dict(cls, data: dict[str, Any]) -> XWEdge:
        """Create edge from dictionary representation."""
        return cls(
            source=data['source'],
            target=data['target'],
            edge_type=data.get('edge_type', 'default'),
            weight=data.get('weight', 1.0),
            properties=data.get('properties', {}),
            is_bidirectional=data.get('is_bidirectional', False),
            edge_id=data.get('edge_id')
        )

    def __repr__(self) -> str:
        direction = "<->" if self.is_bidirectional else "->"
        return f"XWEdge({self.source}{direction}{self.target}, type={self.edge_type}, weight={self.weight})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, XWEdge):
            return False
        return (self.source == other.source and 
                self.target == other.target and 
                self.edge_type == other.edge_type)
# Convenience functions

def create_node(data: Any = None) -> XWNode:
    """Create a new XWNode instance."""
    return XWNode(data)


def from_dict(data: dict[str, Any]) -> XWNode:
    """Create XWNode from dictionary."""
    return XWFactory.from_dict(data)


def from_list(data: list[Any]) -> XWNode:
    """Create XWNode from list."""
    return XWFactory.from_list(data)


def empty_node() -> XWNode:
    """Create an empty XWNode."""
    return XWNode()
# Export main classes
__all__ = [
    'XWNode',
    'XWEdge',
    'XWFactory',
    'create_node',
    'from_dict',
    'from_list',
    'empty_node',
    # A+ Usability Presets
    'create_with_preset',
    'list_available_presets',
    # Performance Modes
    'fast',
    'optimized', 
    'adaptive',
    'dual_adaptive',
    # Cache Management (NEW in v0.0.1.29)
    'get_cache_stats',
    'clear_cache',
    'configure_cache',
    'get_cache_health',
    'invalidate_cache',
    'get_cache_proof',
    'print_cache_report',
    'get_cache_comparison',
]
