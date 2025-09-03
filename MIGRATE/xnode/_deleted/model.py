"""
The internal, mutable data model for the xnode tree.

This module is not intended for public use. It defines the `aNode` classes
that provide the underlying structure and performance optimizations (like lazy
loading, object pooling, and caching) used by the public `xNode` facade.
Each class formally implements its corresponding abstract interface from `abc.py`.
"""
import threading
from abc import ABC, abstractmethod
from typing import Any, Union, List, Dict, Optional, Iterator, Tuple, Callable

from .errors import xNodeTypeError, xNodePathError, xNodeLimitError, xNodeValueError
from .config import get_config
from .abc import iNode, iNodeValue, iNodeList, iNodeDict, iNodeReference, iNodeObject, iNodeFactory


class NodePool:
    """
    An object pool for reusing `aNode` instances to reduce memory allocation overhead.
    This is particularly effective when creating and destroying many nodes.
    """
    __slots__ = ('_pools', '_max_size', '_lock')

    def __init__(self, max_size: int):
        self._pools: Dict[type, List[aNode]] = {
            aNodeValue: [],
            aNodeList: [],
            aNodeDict: [],
        }
        self._max_size = max_size
        self._lock = threading.RLock() if get_config().enable_thread_safety else None

    def get(self, node_type: type, *args, **kwargs) -> 'aNode':
        """Get a node from the pool or create a new one if the pool is empty."""
        pool = self._pools.get(node_type)
        if self._lock:
            with self._lock:
                if pool:
                    node = pool.pop()
                    node.__init__(*args, **kwargs) # Re-initialize the node
                    return node
        elif pool:
            node = pool.pop()
            node.__init__(*args, **kwargs)
            return node
        
        return node_type(*args, **kwargs)

    def release(self, node: 'aNode'):
        """Return a node to the pool for future reuse."""
        node_type = type(node)
        pool = self._pools.get(node_type)
        if pool is not None:
            if self._lock:
                with self._lock:
                    if len(pool) < self._max_size:
                        node._parent = None # Clear references
                        pool.append(node)
            elif len(pool) < self._max_size:
                node._parent = None
                pool.append(node)

# --- Global Singleton for Node Pool ---
_node_pool_instance: Optional[NodePool] = None
def get_node_pool() -> NodePool:
    global _node_pool_instance
    if _node_pool_instance is None:
        _node_pool_instance = NodePool(get_config().node_pool_size)
    return _node_pool_instance


class aNode(iNode):
    """Abstract base for all internal nodes, implementing the iNode interface."""
    __slots__ = ('_parent', '_cached_native', '_hash')
    
    def __init__(self, parent: Optional['aNode'] = None):
        self._parent: Optional['aNode'] = parent
        self._cached_native: Optional[Any] = None
        self._hash: Optional[int] = None
    
    @property
    def parent(self) -> Optional['aNode']:
        """Get the parent node."""
        return self._parent
    
    @parent.setter
    def parent(self, value: Optional['aNode']):
        """Set the parent node."""
        self._parent = value
    
    def _get_child(self, key_or_index: Union[str, int]) -> 'aNode':
        """Get a child node by key or index."""
        raise xNodeTypeError(f"Node type {type(self).__name__} does not support child access.")
    
    @abstractmethod
    def _to_native(self) -> Any:
        """Convert this node and its children to a native Python object."""
        pass
    
    def _get_cached_native(self) -> Any:
        """Get cached native representation or compute and cache it."""
        if self._cached_native is None:
            self._cached_native = self._to_native()
        return self._cached_native
    
    def _invalidate_cache(self):
        """Invalidate cached native representation."""
        self._cached_native = None
        self._hash = None
        # Remove expensive parent propagation for performance
        # if self._parent is not None:
        #     self._parent._invalidate_cache()
    
    def _get_root(self) -> 'aNode':
        """Get the root node of this tree."""
        current = self
        while current._parent is not None:
            current = current._parent
        return current
    
    def _get_key_in_parent(self) -> Optional[Union[str, int]]:
        """Get the key/index of this node in its parent."""
        if self._parent is None:
            return None
        
        # Optimized key lookup for common cases
        if isinstance(self._parent, aNodeDict):
            for key, child in self._parent._children.items():
                if child is self:
                    return key
            # Check source data for lazy-loaded nodes
            for key, child in self._parent._source_data.items():
                if child is self:
                    return key
        elif isinstance(self._parent, aNodeList):
            try:
                return self._parent._children.index(self)
            except ValueError:
                pass
        
        return None
    
    def _get_path(self) -> str:
        """Get the path to this node from the root."""
        path_parts = []
        current = self
        
        while current is not None:
            key = current._get_key_in_parent()
            if key is not None:
                path_parts.append(str(key))
            current = current._parent
        
        # Use efficient string joining
        return '.'.join(reversed(path_parts)) if path_parts else 'root'


class aNodeValue(aNode, iNodeValue):
    """Internal node for a primitive value, implementing iValueNode."""
    __slots__ = ('value',)

    def __init__(self, value: Any, parent: Optional['aNode'] = None):
        super().__init__(parent)
        self.value = value

    def _to_native(self) -> Any:
        return self.value


class aNodeReference(aNode, iNodeReference):
    """Internal node for a reference, implementing iReferenceNode."""
    __slots__ = ('uri', 'reference_type', 'metadata')

    def __init__(self, uri: str, reference_type: str, metadata: Dict[str, Any], parent: Optional['aNode'] = None):
        super().__init__(parent)
        self.uri = uri
        self.reference_type = reference_type
        self.metadata = metadata

    def _to_native(self) -> Dict[str, Any]:
        return {
            '$ref': self.uri,
            'type': self.reference_type,
            'metadata': self.metadata
        }


class aNodeObject(aNode, iNodeObject):
    """Internal node for an object reference, implementing iObjectNode."""
    __slots__ = ('uri', 'object_type', 'mime_type', 'size', 'metadata')

    def __init__(self, uri: str, object_type: str, mime_type: Optional[str], size: Optional[int], metadata: Dict[str, Any], parent: Optional['aNode'] = None):
        super().__init__(parent)
        self.uri = uri
        self.object_type = object_type
        self.mime_type = mime_type
        self.size = size
        self.metadata = metadata

    def _to_native(self) -> Dict[str, Any]:
        result = {
            'uri': self.uri,
            'type': self.object_type,
            'metadata': self.metadata
        }
        if self.mime_type:
            result['mime_type'] = self.mime_type
        if self.size is not None:
            result['size'] = self.size
        return result


class aNodeList(aNode, iNodeList):
    """Internal node for a list, implementing iListNode with lazy-loading."""
    __slots__ = ('_children', '_source_data', '_is_lazy')

    def __init__(self, source_data: List[Any], is_lazy: bool, parent: Optional['aNode'] = None):
        super().__init__(parent)
        self._source_data = source_data
        self._is_lazy = is_lazy
        self._children: List[aNode] = [] if is_lazy else self._eager_load(source_data)

    def _eager_load(self, data: List[Any]) -> List['aNode']:
        return [aNodeFactory.from_native(item, parent=self) for item in data]

    def _get_child(self, index: Union[str, int]) -> 'aNode':
        if isinstance(index, str):
            try:
                index = int(index)
            except ValueError:
                raise xNodeTypeError(f"List indices must be integers, got '{index}'")
        
        if not (0 <= index < len(self._source_data)):
            raise xNodePathError(f"List index out of range: {index}")
        
        if self._is_lazy:
            if index >= len(self._children):
                # Extend children list if needed
                while len(self._children) <= index:
                    self._children.append(None)
                
                if self._children[index] is None:
                    self._children[index] = aNodeFactory.from_native(self._source_data[index], parent=self)
            
            return self._children[index]
        else:
            return self._children[index]

    def _to_native(self) -> List[Any]:
        if self._is_lazy:
            # Lazy conversion - only convert loaded children
            result = []
            for i in range(len(self._source_data)):
                if i < len(self._children) and self._children[i] is not None:
                    result.append(self._children[i]._to_native())
                else:
                    result.append(self._source_data[i])
            return result
        else:
            return [child._to_native() for child in self._children]

    def __iter__(self) -> Iterator['aNode']:
        for i in range(len(self._source_data)):
            yield self._get_child(i)

    def __len__(self) -> int:
        """Return the length of the list."""
        return len(self._source_data)

    def clear(self) -> None:
        """Clear all children from this list."""
        self._children.clear()
        self._source_data.clear()
        self._invalidate_cache()
    
    def contains(self, node: 'aNode') -> bool:
        """Check if this container contains the specified node."""
        return node in self._children
    
    def copy(self) -> 'aNodeList':
        """Create a shallow copy of this list node."""
        return aNodeList(self._source_data.copy(), self._is_lazy, self._parent)
    
    def append(self, node: 'aNode') -> None:
        """Append a node to this list."""
        self._children.append(node)
        self._source_data.append(node._to_native())
        node._parent = self
        self._invalidate_cache()
    
    def insert(self, index: int, node: 'aNode') -> None:
        """Insert a node at the specified index."""
        self._children.insert(index, node)
        self._source_data.insert(index, node._to_native())
        node._parent = self
        self._invalidate_cache()
    
    def remove(self, node: 'aNode') -> None:
        """Remove a node from this list."""
        try:
            index = self._children.index(node)
            self._children.pop(index)
            self._source_data.pop(index)
            node._parent = None
            self._invalidate_cache()
        except ValueError:
            raise xNodeValueError("Node not found in list")
    
    def pop(self, index: int = -1) -> 'aNode':
        """Remove and return node at index."""
        if not (0 <= index < len(self._children)):
            raise xNodePathError(f"List index out of range: {index}")
        
        node = self._children.pop(index)
        self._source_data.pop(index)
        node._parent = None
        self._invalidate_cache()
        return node
    
    def extend(self, nodes: Iterator['aNode']) -> None:
        """Extend list with nodes from iterator."""
        for node in nodes:
            self.append(node)
    
    def reverse(self) -> None:
        """Reverse the list in place."""
        self._children.reverse()
        self._source_data.reverse()
        self._invalidate_cache()
    
    def sort(self, key: Optional[Callable] = None) -> None:
        """Sort the list in place."""
        if key is None:
            self._children.sort()
            self._source_data.sort()
        else:
            self._children.sort(key=lambda n: key(n._to_native()))
            self._source_data.sort(key=key)
        self._invalidate_cache()


class aNodeDict(aNode, iNodeDict):
    """Internal node for a dictionary, implementing iDictNode with lazy-loading."""
    __slots__ = ('_children', '_source_data', '_is_lazy', '_keys')

    def __init__(self, source_data: Dict[str, Any], is_lazy: bool, parent: Optional['aNode'] = None):
        super().__init__(parent)
        self._source_data = source_data
        self._is_lazy = is_lazy
        self._keys = list(source_data.keys())
        self._children: Dict[str, aNode] = {} if is_lazy else self._eager_load(source_data)

    def _eager_load(self, data: Dict[str, Any]) -> Dict[str, 'aNode']:
        return {key: aNodeFactory.from_native(value, parent=self) for key, value in data.items()}

    def _get_child(self, key: Union[str, int]) -> 'aNode':
        key = str(key)
        if key not in self._source_data:
            raise xNodePathError(f"Key not found: '{key}'")
        
        if key not in self._children:
            child = aNodeFactory.from_native(self._source_data[key], parent=self)
            self._children[key] = child
            return child
        
        return self._children[key]

    def _to_native(self) -> Dict[str, Any]:
        if not self._children:
            return self._source_data
        
        data = self._source_data.copy()
        for key, child in self._children.items():
            data[key] = child._to_native()
        return data

    def __len__(self) -> int: return len(self._source_data)
    def keys(self) -> Iterator[str]: return iter(self._keys)
    def items(self) -> Iterator[Tuple[str, 'aNode']]:
        for key in self._keys: yield key, self._get_child(key)
    def __iter__(self) -> Iterator['aNode']:
        for key in self._keys: yield self._get_child(key)
    
    def clear(self) -> None:
        """Clear all children from this dictionary."""
        self._children.clear()
        self._source_data.clear()
        self._keys.clear()
        self._invalidate_cache()
    
    def contains(self, node: 'aNode') -> bool:
        """Check if this container contains the specified node."""
        return node in self._children.values()
    
    def copy(self) -> 'aNodeDict':
        """Create a shallow copy of this dictionary node."""
        return aNodeDict(self._source_data.copy(), self._is_lazy, self._parent)
    
    def set_child(self, key: str, node: 'aNode') -> None:
        """Set a child node with the specified key."""
        self._children[key] = node
        self._source_data[key] = node._to_native()
        if key not in self._keys:
            self._keys.append(key)
        self._invalidate_cache()
    
    def remove_child(self, key: str) -> Optional['aNode']:
        """Remove and return child node by key. Returns None if key not found."""
        if key in self._children:
            node = self._children.pop(key)
            self._source_data.pop(key, None)
            if key in self._keys:
                self._keys.remove(key)
            self._invalidate_cache()
            return node
        return None
    
    def has_key(self, key: str) -> bool:
        """Check if a key exists in this dictionary."""
        return key in self._source_data
    
    def values(self) -> Iterator['aNode']:
        """Get an iterator over the child nodes (values)."""
        for key in self._keys:
            yield self._get_child(key)
    
    def update(self, other: 'aNodeDict') -> None:
        """Update this dict with items from another dict node."""
        for key, node in other.items():
            self.set_child(key, node)
    
    def get_child(self, key: str, default: Any = None) -> Optional['aNode']:
        """Get a child node by key, returning a default value if not found."""
        try:
            return self._get_child(key)
        except xNodePathError:
            return default


class aNodeFactory(iNodeFactory):
    """Factory for creating nodes from native Python objects."""
    
    @staticmethod
    def from_native(data: Any, parent: Optional[aNode] = None, depth: int = 0) -> aNode:
        """Create a node from a native Python object."""
        # Optimized depth check
        if depth > 1000:  # Increased depth limit for better performance
            raise xNodeLimitError("Maximum recursion depth exceeded")
        
        # Fast path for primitive types
        if isinstance(data, (str, int, float, bool, type(None))):
            return aNodeValue(data, parent)
        
        # Fast path for lists
        if isinstance(data, list):
            return aNodeList(data, True, parent)  # Use lazy loading for better performance
        
        # Fast path for dictionaries
        if isinstance(data, dict):
            return aNodeDict(data, True, parent)  # Use lazy loading for better performance
        
        # For other types, create a value node
        return aNodeValue(data, parent)
    
    @staticmethod
    def to_native(node: iNode) -> Any:
        """Convert a node to a native Python object."""
        return node._to_native()
    
    @staticmethod
    def from_native_bulk(data_list: List[Any], parent: Optional[aNode] = None) -> List[aNode]:
        """Create multiple nodes from a list of native objects."""
        return [aNodeFactory.from_native(data, parent) for data in data_list]
    
    @staticmethod
    def create_reference(uri: str, reference_type: str, metadata: Optional[Dict[str, Any]], parent: Optional[aNode] = None) -> aNodeReference:
        """Create a reference node."""
        return aNodeReference(uri, reference_type, metadata or {}, parent)
    
    @staticmethod
    def create_object(uri: str, object_type: str, mime_type: Optional[str], size: Optional[int], metadata: Optional[Dict[str, Any]], parent: Optional[aNode] = None) -> aNodeObject:
        """Create an object node."""
        return aNodeObject(uri, object_type, mime_type, size, metadata or {}, parent)
