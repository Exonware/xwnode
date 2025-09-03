#!/usr/bin/env python3
"""
xNode Facade - Public API for xNode.

This module provides the public interface for xNode, extending aNode
to provide additional functionality and a clean public API.
"""

import threading
import copy
from typing import Any, Iterator, Union, Optional, List, Dict, Callable, Tuple
from collections import OrderedDict
from functools import lru_cache
import time
import weakref

# Core xNode imports
from .errors import (
    xNodeTypeError, xNodePathError, xNodeSecurityError, xNodeValueError, xNodeLimitError
)
from .config import get_config
from .protocols import iNodeFacade
from .base import aNode, aEdge, aQuery, aQueryResult, aQueryEngine

# System-level imports - reuse xSystem capabilities
from exonware.xsystem.security import get_resource_limits
from exonware.xsystem.validation import validate_untrusted_data
from exonware.xsystem.monitoring import create_component_metrics
from exonware.xsystem import get_logger

logger = get_logger('xnode.facade')

# Metrics setup
_metrics = create_component_metrics('xnode_facade')
measure_operation = _metrics['measure_operation']
record_cache_hit = _metrics['record_cache_hit']
record_cache_miss = _metrics['record_cache_miss']


class EnhancedPathParser:
    """Enhanced path parser supporting multiple separators and caching."""
    
    def __init__(self, max_cache_size: int = 1024):
        self._cache: OrderedDict = OrderedDict()
        self._max_cache_size = max_cache_size
        self._lock = threading.RLock()
        # Support both . and / separators
        self._separators = './'
    
    def parse(self, path: str) -> List[str]:
        """Parse path with enhanced separator support."""
        if not path or path in ('.', '/'):
            return []
        
        with self._lock:
            if path in self._cache:
                record_cache_hit()
                # Move to end (LRU)
                self._cache.move_to_end(path)
                return self._cache[path]
            
            record_cache_miss()
            segments = self._parse_path(path)
            
            # Cache result
            if len(self._cache) >= self._max_cache_size:
                self._cache.popitem(last=False)  # Remove oldest
            self._cache[path] = segments
            
            return segments
    
    def _parse_path(self, path: str) -> List[str]:
        """Enhanced path parsing supporting . and / separators."""
        # Handle empty or root paths
        if not path or path in ('.', '/'):
            return []
        
        # Support both . and / as separators
        # First normalize to use . as separator
        normalized_path = path.replace('/', '.')
        
        # Split and filter out empty segments
        segments = [seg for seg in normalized_path.split('.') if seg]
        
        return segments


# Global instances
_enhanced_path_parser: Optional[EnhancedPathParser] = None

def get_enhanced_path_parser() -> EnhancedPathParser:
    """Get global enhanced path parser instance."""
    global _enhanced_path_parser
    if _enhanced_path_parser is None:
        _enhanced_path_parser = EnhancedPathParser()
    return _enhanced_path_parser


class xNode(aNode):
    """
    xNode Facade - Public API for xNode.
    
    This facade extends aNode to provide additional functionality and
    a clean public API while maintaining performance and usability.
    
    Features:
    - Enhanced path parsing
    - Performance tracking
    - Comprehensive error handling
    - Fluent API design
    """
    
    __slots__ = ('_frozen', '_perf', '_performance_manager', '_query')
    
    def __init__(self, data: Any = None):
        """Initialize xNode with data."""
        
        # Performance tracking
        self._perf = {
            'ops': 0, 'find': 0, 'set': 0, 'get': 0,
            'cache_hits': 0, 'cache_misses': 0
        }
        
        # State flags
        self._frozen = False
        self._performance_manager = None
        self._query = None
        
        # Initialize with strategy
        if data is not None:
            super().__init__(self._create_strategy_from_data(data))
        else:
            from .strategies.simple import SimpleNodeStrategy
            super().__init__(SimpleNodeStrategy({}))
    
    def _create_strategy_from_data(self, data: Any):
        """Create strategy from data."""
        from .strategies.simple import SimpleNodeStrategy
        return SimpleNodeStrategy.create_from_data(data)

    @classmethod
    def from_native(cls, data: Any) -> 'xNode':
        """Create xNode from native Python data."""
        return cls(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'xNode':
        """Create xNode from dictionary."""
        return cls(data)
    
    @classmethod
    def from_list(cls, data: List[Any]) -> 'xNode':
        """Create xNode from list."""
        return cls(data)
    
    @classmethod
    def empty(cls) -> 'xNode':
        """Create empty xNode."""
        return cls({})
    
    # Enhanced navigation methods
    def find(self, path: str, default: Any = None) -> Optional['xNode']:
        """
        Find a node by path with enhanced path parsing.
        
        Args:
            path: Path to find (supports . and / separators)
            default: Default value if path not found
            
        Returns:
            xNode instance or None
        """
        self._perf['find'] += 1
        self._perf['ops'] += 1
        
        try:
            # Use enhanced path parser
            parser = get_enhanced_path_parser()
            segments = parser.parse(path)
            
            if not segments:
                return self
            
            current = self
            for segment in segments:
                if current is None:
                    break
                current = current.get(segment)
            
            return current if current is not None else (xNode(default) if default is not None else None)
            
        except Exception as e:
            logger.debug(f"Find operation failed for path '{path}': {e}")
            return xNode(default) if default is not None else None
    
    def get(self, path: str, default: Any = None) -> Optional['xNode']:
        """Get a node by path."""
        self._perf['get'] += 1
        self._perf['ops'] += 1
        
        try:
            result = super().get(path, default)
            if result is None and default is not None:
                return xNode(default)
            return xNode(result._strategy) if result else None
        except Exception:
            return xNode(default) if default is not None else None
    
    def set(self, path: str, value: Any, in_place: bool = True) -> 'xNode':
        """Set a value at path."""
        self._perf['set'] += 1
        self._perf['ops'] += 1
        
        if self._frozen:
            raise xNodeSecurityError("Cannot modify frozen xNode")
        
        try:
            result = super().set(path, value, in_place)
            return self if in_place else xNode(result._strategy)
        except Exception as e:
            logger.debug(f"Set operation failed for path '{path}': {e}")
            return self
    
    def put(self, path: str, value: Any) -> 'xNode':
        """Put a value at path (alias for set with in_place=True)."""
        return self.set(path, value, in_place=True)
    
    def delete(self, path: str, in_place: bool = True) -> 'xNode':
        """Delete a node at path."""
        self._perf['ops'] += 1
        
        if self._frozen:
            raise xNodeSecurityError("Cannot modify frozen xNode")
        
        try:
            result = super().delete(path, in_place)
            return self if in_place else xNode(result._strategy)
        except Exception as e:
            logger.debug(f"Delete operation failed for path '{path}': {e}")
            return self
    
    def remove(self, path: str) -> 'xNode':
        """Remove a node at path (alias for delete with in_place=True)."""
        return self.delete(path, in_place=True)
    
    # Navigation shortcuts
    def __getitem__(self, key: Union[str, int]) -> 'xNode':
        """Get child by key or index."""
        try:
            result = super().__getitem__(key)
            return xNode(result._strategy)
        except Exception:
            raise xNodePathError(str(key), reason="not_found")
    
    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """Set child by key or index."""
        if self._frozen:
            raise xNodeSecurityError("Cannot modify frozen xNode")
        super().__setitem__(key, value)
    
    # Utility methods
    def freeze(self) -> 'xNode':
        """Make this xNode immutable."""
        self._frozen = True
        return self
    
    def unfreeze(self) -> 'xNode':
        """Make this xNode mutable."""
        self._frozen = False
        return self
    
    @property
    def is_frozen(self) -> bool:
        """Check if this xNode is frozen."""
        return self._frozen
    
    def clone(self) -> 'xNode':
        """Create a deep copy of this xNode."""
        return xNode(self.to_native())
    
    def copy(self) -> 'xNode':
        """Create a copy of this xNode."""
        return self.clone()
    
    # Performance methods
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return dict(self._perf)
    
    def reset_performance_stats(self) -> 'xNode':
        """Reset performance statistics."""
        self._perf = {
            'ops': 0, 'find': 0, 'set': 0, 'get': 0,
            'cache_hits': 0, 'cache_misses': 0
        }
        return self
    
    # Query interface
    def query(self, query_string: str, **kwargs) -> 'xNodeQuery':
        """Create a query interface for this node."""
        return xNodeQuery(self)
    
    # Enhanced string representation
    def __repr__(self) -> str:
        """String representation."""
        type_name = self.type
        if self.is_leaf:
            return f"xNode({type_name}: {repr(self.value)})"
        else:
            count = len(self)
            return f"xNode({type_name}: {count} items)"
    
    def __str__(self) -> str:
        """String representation."""
        return self.__repr__()


class xNodeQuery:
    """Query interface for xNode."""
    
    def __init__(self, node: xNode):
        self._node = node
    
    def find_by_value(self, value: Any) -> List[xNode]:
        """Find nodes by value."""
        results = []
        
        def _search(node: xNode, path: str = ""):
            if node.is_leaf and node.value == value:
                results.append(node)
            else:
                for key in node.keys() if hasattr(node, 'keys') else []:
                    child = node.get(str(key))
                    if child:
                        _search(child, f"{path}.{key}" if path else str(key))
        
        _search(self._node)
        return results
    
    def find_by_type(self, node_type: str) -> List[xNode]:
        """Find nodes by type."""
        results = []
        
        def _search(node: xNode):
            if node.type == node_type:
                results.append(node)
            
            for child in node:
                _search(child)
        
        _search(self._node)
        return results
    
    def count(self, predicate: Optional[Callable[[xNode], bool]] = None) -> int:
        """Count nodes matching predicate."""
        if predicate is None:
            return len(self._node)
        
        count = 0
        def _count(node: xNode):
            nonlocal count
            if predicate(node):
                count += 1
            for child in node:
                _count(child)
        
        _count(self._node)
        return count


class xNodeFactory:
    """Factory for creating xNode instances."""
    
    @staticmethod
    def create(data: Any = None) -> xNode:
        """Create xNode from data."""
        return xNode(data)
    
    @staticmethod
    def from_json(json_str: str) -> xNode:
        """Create xNode from JSON string."""
        import json
        try:
            data = json.loads(json_str)
            return xNode(data)
        except Exception as e:
            raise xNodeValueError(f"Invalid JSON: {e}")
    
    @staticmethod
    def from_yaml(yaml_str: str) -> xNode:
        """Create xNode from YAML string."""
        try:
            import yaml
            data = yaml.safe_load(yaml_str)
            return xNode(data)
        except ImportError:
            raise xNodeValueError("PyYAML not installed")
        except Exception as e:
            raise xNodeValueError(f"Invalid YAML: {e}")
    
    @staticmethod
    def empty() -> xNode:
        """Create empty xNode."""
        return xNode({})
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> xNode:
        """Create xNode from dictionary."""
        return xNode(data)
    
    @staticmethod
    def from_list(data: List[Any]) -> xNode:
        """Create xNode from list."""
        return xNode(data)


# Convenience functions
def create_node(data: Any = None) -> xNode:
    """Create xNode from data."""
    return xNode(data)

def from_dict(data: Dict[str, Any]) -> xNode:
    """Create xNode from dictionary."""
    return xNode(data)

def from_list(data: List[Any]) -> xNode:
    """Create xNode from list."""
    return xNode(data)

def empty_node() -> xNode:
    """Create empty xNode."""
    return xNode({})


# Export main classes
__all__ = [
    'xNode',
    'xNodeQuery', 
    'xNodeFactory',
    'create_node',
    'from_dict',
    'from_list',
    'empty_node'
]
