#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/base.py

Node Strategy Base Classes - Production-Grade Implementation

This module defines the complete abstract base class hierarchy for all node strategies:
- ANodeStrategy: Universal base with full iNodeStrategy implementation
- ANodeLinearStrategy: Linear data structures (Stack, Queue, Deque, PriorityQueue)
- ANodeMatrixStrategy: Matrix data structures (SparseMatrix, Bitmap, etc.)
- ANodeGraphStrategy: Graph data structures (AdjacencyList, UnionFind)
- ANodeTreeStrategy: Tree data structures (BTree, Trie, Heap, etc.)

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 22-Oct-2025
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Iterator, Union, AsyncIterator
import asyncio

from .contracts import NodeType, INodeStrategy
from ...defs import NodeMode, NodeTrait
from ...errors import XWNodeUnsupportedCapabilityError


class ANodeStrategy(INodeStrategy):
    """
    Production-grade base strategy for ALL node implementations.
    
    This class provides:
    - Complete iNodeStrategy interface implementation
    - Default implementations for common operations
    - Trait validation and capability checking
    - Performance metadata and metrics
    - Factory methods for strategy creation
    
    Follows eXonware Priorities:
    1. Security: Trait validation, safe operations
    2. Usability: Clear interface, helpful errors
    3. Maintainability: Clean base implementation
    4. Performance: Efficient default methods
    5. Extensibility: Easy to override and extend
    """
    
    # Strategy type classification (must be overridden by subclasses)
    STRATEGY_TYPE: NodeType = NodeType.TREE  # Default for backward compatibility
    
    # Make NodeType available to all subclasses
    NodeType = NodeType
    
    def __init__(self, mode: NodeMode, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize the node strategy.
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        
        Args:
            mode: The NodeMode for this strategy
            traits: NodeTrait flags for this strategy
            **options: Additional strategy-specific options
        
        Root cause fixed: Remove 'mode' and 'traits' from options if present
        to prevent "multiple values for argument" errors when strategy classes
        pass these explicitly and also include them in **options.
        """
        # Root cause fixed: Remove 'mode' and 'traits' from options to prevent conflicts
        # These are passed explicitly as parameters, not as part of options
        # Performance optimization: Check if options is empty first, then check keys
        # (dict 'in' operator is O(1) average case, faster than set creation for small dicts)
        if options and ('mode' in options or 'traits' in options):
            clean_options = {k: v for k, v in options.items() if k not in ('mode', 'traits')}
        else:
            clean_options = options  # Reuse original dict - no copy needed
        
        self.mode = mode
        self.traits = traits
        self.options = clean_options
        self._data: dict[str, Any] = {}
        self._size = 0
        
        # Root cause fixed: Trait validation runs on every strategy initialization
        # Performance optimization: Make validation optional via validate_traits option
        # Default to True for safety, but can be disabled for performance-critical paths
        validate_traits = clean_options.get('validate_traits', True)
        if validate_traits:
            self._validate_traits()
    
    def _validate_traits(self) -> None:
        """
        Validate that the requested traits are compatible with this strategy.
        
        Time Complexity: O(t) where t is number of trait flags
        
        Performance optimization: Can be disabled via validate_traits=False option
        in __init__ for performance-critical paths where traits are known to be valid.
        """
        supported_traits = self.get_supported_traits()
        unsupported = self.traits & ~supported_traits
        if unsupported != NodeTrait.NONE:
            unsupported_names = [trait.name for trait in NodeTrait if trait in unsupported]
            raise ValueError(f"Strategy {self.mode.name} does not support traits: {unsupported_names}")
    
    def get_supported_traits(self) -> NodeTrait:
        """
        Get the traits supported by this strategy implementation (override in subclasses).
        
        Time Complexity: O(1)
        """
        return NodeTrait.NONE
    
    def has_trait(self, trait: NodeTrait) -> bool:
        """
        Check if this strategy has a specific trait.
        
        Time Complexity: O(1)
        """
        return bool(self.traits & trait)
    
    def require_trait(self, trait: NodeTrait, operation: str = "operation") -> None:
        """
        Require a specific trait for an operation.
        
        Time Complexity: O(1)
        """
        if not self.has_trait(trait):
            raise XWNodeUnsupportedCapabilityError(
                operation,
                self.mode.name,
                [t.name for t in NodeTrait if t in self.traits]
            )
    
    # ============================================================================
    # CORE OPERATIONS (Must be implemented by concrete strategies)
    # ============================================================================
    
    @abstractmethod
    def put(self, key: Any, value: Any = None) -> None:
        """
        Store a key-value pair.
        
        Args:
            key: The key to store
            value: The value to associate with the key
        """
        pass
    
    @abstractmethod
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Retrieve a value by key.
        
        Args:
            key: The key to look up
            default: Default value if key not found
            
        Returns:
            The value associated with the key, or default if not found
        """
        pass
    
    @abstractmethod
    def has(self, key: Any) -> bool:
        """
        Check if a key exists.
        
        Args:
            key: The key to check
            
        Returns:
            True if key exists, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, key: Any) -> bool:
        """
        Remove a key-value pair.
        
        Args:
            key: The key to remove
            
        Returns:
            True if key was found and removed, False otherwise
        """
        pass
    
    @abstractmethod
    def keys(self) -> Iterator[Any]:
        """Get an iterator over all keys."""
        pass
    
    @abstractmethod
    def values(self) -> Iterator[Any]:
        """Get an iterator over all values."""
        pass
    
    @abstractmethod
    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get an iterator over all key-value pairs."""
        pass
    
    @abstractmethod
    def __len__(self) -> int:
        """Get the number of key-value pairs."""
        pass
    
    @abstractmethod
    def to_native(self) -> Any:
        """Convert to native Python object."""
        pass
    
    # ============================================================================
    # DEFAULT IMPLEMENTATIONS (INodeStrategy interface compatibility)
    # ============================================================================
    
    def insert(self, key: Any, value: Any) -> None:
        """
        Insert key-value pair (INodeStrategy interface method).
        Delegates to put() for compatibility.
        
        Time Complexity: Same as put()
        """
        self.put(key, value)
    
    def find(self, key: Any) -> Optional[Any]:
        """
        Find value by key (INodeStrategy interface method).
        Delegates to get() for compatibility.
        
        Time Complexity: Same as get()
        """
        return self.get(key)
    
    def size(self) -> int:
        """
        Get size (INodeStrategy interface method).
        Delegates to __len__() for compatibility.
        
        Time Complexity: O(1)
        """
        return len(self)
    
    def is_empty(self) -> bool:
        """
        Check if empty (INodeStrategy interface method).
        
        Time Complexity: O(1)
        """
        return len(self) == 0
    
    def exists(self, path: str) -> bool:
        """
        Check if path exists (default implementation).
        
        Time Complexity: Depends on get() implementation
        """
        return self.get(path) is not None
    
    @classmethod
    def create_from_data(cls, data: Any) -> 'ANodeStrategy':
        """
        Create a new strategy instance from data.
        
        Time Complexity: O(n) where n is size of data
        
        Args:
            data: The data to create the strategy from
            
        Returns:
            A new strategy instance containing the data
        """
        instance = cls()
        if isinstance(data, dict):
            for key, value in data.items():
                instance.put(key, value)
        elif isinstance(data, (list, tuple)):
            for i, value in enumerate(data):
                instance.put(i, value)
        else:
            # For primitive values, store as root value
            instance.put('_value', data)
        return instance
    
    def clear(self) -> None:
        """
        Clear all data (default implementation).
        
        Time Complexity: O(1)
        """
        self._data.clear()
        self._size = 0
    
    def __contains__(self, key: Any) -> bool:
        """
        Check if key exists (default implementation).
        
        Time Complexity: Depends on has() implementation
        """
        return self.has(key)
    
    def __getitem__(self, key: Any) -> Any:
        """
        Get value by key (default implementation).
        
        Time Complexity: Depends on get() implementation
        """
        return self.get(key)
    
    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set value by key (default implementation).
        
        Time Complexity: Depends on put() implementation
        """
        self.put(key, value)
    
    def __delitem__(self, key: Any) -> None:
        """
        Delete key (default implementation).
        
        Time Complexity: Depends on delete() implementation
        """
        if not self.delete(key):
            raise KeyError(key)
    
    def __iter__(self) -> Iterator[Any]:
        """
        Iterate over keys (default implementation).
        
        Time Complexity: Depends on keys() implementation
        """
        return self.keys()
    
    def __str__(self) -> str:
        """
        String representation (default implementation).
        
        Time Complexity: O(1)
        """
        return f"{self.__class__.__name__}(mode={self.mode.name}, size={len(self)})"
    
    def __repr__(self) -> str:
        """
        Detailed string representation (default implementation).
        
        Time Complexity: O(1)
        """
        return f"{self.__class__.__name__}(mode={self.mode.name}, traits={self.traits}, size={len(self)})"
    
    # ============================================================================
    # TYPE CHECKING PROPERTIES (Default implementations for iNodeStrategy)
    # ============================================================================
    
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (default: false)."""
        return len(self) == 0
    
    @property
    def is_list(self) -> bool:
        """Check if this is a list node (default: false, override in list strategies)."""
        return False
    
    @property
    def is_dict(self) -> bool:
        """Check if this is a dict node (default: true for most strategies)."""
        return True
    
    @property
    def is_reference(self) -> bool:
        """Check if this is a reference node (default: false)."""
        return False
    
    @property
    def is_object(self) -> bool:
        """Check if this is an object node (default: false)."""
        return False
    
    @property
    def type(self) -> str:
        """Get the type of this node (default: 'dict')."""
        return "dict"
    
    @property
    def value(self) -> Any:
        """Get the value of this node (default: native representation)."""
        return self.to_native()
    
    # Optional properties with default implementations
    @property
    def uri(self) -> Optional[str]:
        """Get URI (for reference/object nodes)."""
        return None
    
    @property
    def reference_type(self) -> Optional[str]:
        """Get reference type (for reference nodes)."""
        return None
    
    @property
    def object_type(self) -> Optional[str]:
        """Get object type (for object nodes)."""
        return None
    
    @property
    def mime_type(self) -> Optional[str]:
        """Get MIME type (for object nodes)."""
        return None
    
    @property
    def metadata(self) -> Optional[dict[str, Any]]:
        """Get metadata (for reference/object nodes)."""
        return None
    
    # Strategy information
    @property
    def strategy_name(self) -> str:
        """Get the name of this strategy."""
        return self.mode.name
    
    @property
    def supported_traits(self) -> list[NodeTrait]:
        """Get supported traits for this strategy."""
        supported = self.get_supported_traits()
        return [trait for trait in NodeTrait if trait in supported]
    
    # ============================================================================
    # CAPABILITY-BASED OPERATIONS (Default implementations with trait checking)
    # ============================================================================
    
    def get_ordered(self, start: Any = None, end: Any = None) -> list[tuple[Any, Any]]:
        """
        Get items in order (requires ORDERED trait).
        
        Raises:
            XWNodeUnsupportedCapabilityError: If ORDERED trait not supported
        """
        if NodeTrait.ORDERED not in self.traits:
            raise XWNodeUnsupportedCapabilityError("ORDERED", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for ordered strategies
        items = list(self.items())
        if start is not None:
            items = [(k, v) for k, v in items if k >= start]
        if end is not None:
            items = [(k, v) for k, v in items if k < end]
        return items
    
    def get_with_prefix(self, prefix: str) -> list[tuple[Any, Any]]:
        """
        Get items with given prefix (requires HIERARCHICAL trait).
        
        Raises:
            XWNodeUnsupportedCapabilityError: If HIERARCHICAL trait not supported
        """
        if NodeTrait.HIERARCHICAL not in self.traits:
            raise XWNodeUnsupportedCapabilityError("HIERARCHICAL", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for hierarchical strategies
        return [(k, v) for k, v in self.items() if str(k).startswith(prefix)]
    
    def get_priority(self) -> Optional[tuple[Any, Any]]:
        """
        Get highest priority item (requires PRIORITY trait).
        
        Raises:
            XWNodeUnsupportedCapabilityError: If PRIORITY trait not supported
        """
        if NodeTrait.PRIORITY not in self.traits:
            raise XWNodeUnsupportedCapabilityError("PRIORITY", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for priority strategies
        if len(self) == 0:
            return None
        return min(self.items(), key=lambda x: x[0])
    
    def get_weighted(self, key: Any) -> float:
        """
        Get weight for a key (requires WEIGHTED trait).
        
        Raises:
            XWNodeUnsupportedCapabilityError: If WEIGHTED trait not supported
        """
        if NodeTrait.WEIGHTED not in self.traits:
            raise XWNodeUnsupportedCapabilityError("WEIGHTED", self.mode.name, [str(t) for t in self.traits])
        
        # Default implementation for weighted strategies
        return 1.0
    
    # ============================================================================
    # STRATEGY METADATA (Default implementations)
    # ============================================================================
    
    def capabilities(self) -> NodeTrait:
        """Get the capabilities supported by this strategy."""
        return self.traits
    
    def backend_info(self) -> dict[str, Any]:
        """Get information about the backend implementation."""
        return {
            "mode": self.mode.name,
            "traits": str(self.traits),
            "size": len(self),
            "options": self.options.copy() if self.options else {}
        }
    
    def metrics(self) -> dict[str, Any]:
        """Get performance metrics for this strategy."""
        return {
            "size": len(self),
            "mode": self.mode.name,
            "traits": str(self.traits)
        }


# ==============================================================================
# LINEAR DATA STRUCTURE BASE CLASS
# ==============================================================================

class ANodeLinearStrategy(ANodeStrategy):
    """
    Abstract base for linear data structures.
    
    Linear structures include:
    - Stack (LIFO)
    - Queue (FIFO)
    - Deque (Double-ended)
    - Priority Queue (Heap-based)
    - Linked List
    - Array List
    """
    
    # Linear node type
    STRATEGY_TYPE: NodeType = NodeType.LINEAR
    
    # Linear-specific operations (optional - implement if supported)
    @abstractmethod
    def push_front(self, value: Any) -> None:
        """Add element to front."""
        pass
    
    @abstractmethod
    def push_back(self, value: Any) -> None:
        """Add element to back."""
        pass
    
    @abstractmethod
    def pop_front(self) -> Any:
        """Remove element from front."""
        pass
    
    @abstractmethod
    def pop_back(self) -> Any:
        """Remove element from back."""
        pass
    
    @abstractmethod
    def get_at_index(self, index: int) -> Any:
        """Get element at index."""
        pass
    
    @abstractmethod
    def set_at_index(self, index: int, value: Any) -> None:
        """Set element at index."""
        pass
    
    # Behavioral views (optional)
    @abstractmethod
    def as_linked_list(self):
        """Provide LinkedList behavioral view."""
        pass
    
    @abstractmethod
    def as_stack(self):
        """Provide Stack behavioral view."""
        pass
    
    @abstractmethod
    def as_queue(self):
        """Provide Queue behavioral view."""
        pass
    
    @abstractmethod
    def as_deque(self):
        """Provide Deque behavioral view."""
        pass


# ==============================================================================
# MATRIX DATA STRUCTURE BASE CLASS
# ==============================================================================

class ANodeMatrixStrategy(ANodeStrategy):
    """
    Abstract base for matrix data structures.
    
    Matrix structures include:
    - Sparse Matrix (COO, CSR, CSC)
    - Bitmap
    - Roaring Bitmap
    - Dynamic Bitset
    """
    
    # Matrix node type
    STRATEGY_TYPE: NodeType = NodeType.MATRIX
    
    # Matrix-specific operations (must be implemented)
    @abstractmethod
    def get_dimensions(self) -> tuple:
        """Get matrix dimensions (rows, cols)."""
        pass
    
    @abstractmethod
    def get_at_position(self, row: int, col: int) -> Any:
        """Get element at matrix position."""
        pass
    
    @abstractmethod
    def set_at_position(self, row: int, col: int, value: Any) -> None:
        """Set element at matrix position."""
        pass
    
    @abstractmethod
    def get_row(self, row: int) -> list[Any]:
        """Get entire row."""
        pass
    
    @abstractmethod
    def get_column(self, col: int) -> list[Any]:
        """Get entire column."""
        pass
    
    @abstractmethod
    def transpose(self) -> 'ANodeMatrixStrategy':
        """Transpose the matrix."""
        pass
    
    @abstractmethod
    def multiply(self, other: 'ANodeMatrixStrategy') -> 'ANodeMatrixStrategy':
        """Matrix multiplication."""
        pass
    
    @abstractmethod
    def add(self, other: 'ANodeMatrixStrategy') -> 'ANodeMatrixStrategy':
        """Matrix addition."""
        pass
    
    # Matrix behavioral views (optional)
    @abstractmethod
    def as_adjacency_matrix(self):
        """Provide Adjacency Matrix behavioral view."""
        pass
    
    @abstractmethod
    def as_incidence_matrix(self):
        """Provide Incidence Matrix behavioral view."""
        pass
    
    @abstractmethod
    def as_sparse_matrix(self):
        """Provide Sparse Matrix behavioral view."""
        pass


# ==============================================================================
# GRAPH DATA STRUCTURE BASE CLASS
# ==============================================================================

class ANodeGraphStrategy(ANodeStrategy):
    """
    Abstract base for graph data structures.
    
    Graph structures include:
    - Adjacency List
    - Union Find
    """
    
    # Graph node type
    STRATEGY_TYPE: NodeType = NodeType.GRAPH
    
    # Graph-specific operations (must be implemented)
    @abstractmethod
    def add_edge(self, from_node: Any, to_node: Any, weight: float = 1.0) -> None:
        """Add edge between nodes."""
        pass
    
    @abstractmethod
    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        """Remove edge between nodes."""
        pass
    
    @abstractmethod
    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        """Check if edge exists."""
        pass
    
    @abstractmethod
    def find_path(self, start: Any, end: Any) -> list[Any]:
        """Find path between nodes."""
        pass
    
    @abstractmethod
    def get_neighbors(self, node: Any) -> list[Any]:
        """Get neighboring nodes."""
        pass
    
    @abstractmethod
    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        """Get edge weight."""
        pass
    
    # Graph behavioral views (optional)
    @abstractmethod
    def as_union_find(self):
        """Provide Union-Find behavioral view."""
        pass
    
    @abstractmethod
    def as_neural_graph(self):
        """Provide Neural Graph behavioral view."""
        pass
    
    @abstractmethod
    def as_flow_network(self):
        """Provide Flow Network behavioral view."""
        pass


# ==============================================================================
# TREE DATA STRUCTURE BASE CLASS
# ==============================================================================

class ANodeTreeStrategy(ANodeGraphStrategy):
    """
    Abstract base for tree data structures.
    
    Tree structures include:
    - BTree, B+ Tree
    - Trie, Radix Trie, Patricia Trie
    - Heap
    - AVL Tree, Red-Black Tree
    - Skip List, Splay Tree, Treap
    - And many more...
    
    Note: Trees extend Graph because trees ARE graphs (connected acyclic graphs)
    """
    
    # Tree node type
    STRATEGY_TYPE: NodeType = NodeType.TREE
    
    # Tree-specific operations (optional)
    @abstractmethod
    def traverse(self, order: str = 'inorder') -> list[Any]:
        """Traverse tree in specified order (inorder, preorder, postorder)."""
        pass
    
    @abstractmethod
    def get_min(self) -> Any:
        """Get minimum key."""
        pass
    
    @abstractmethod
    def get_max(self) -> Any:
        """Get maximum key."""
        pass
    
    # Tree behavioral views (optional)
    @abstractmethod
    def as_trie(self):
        """Provide Trie behavioral view."""
        pass
    
    @abstractmethod
    def as_heap(self):
        """Provide Heap behavioral view."""
        pass
    
    @abstractmethod
    def as_skip_list(self):
        """Provide SkipList behavioral view."""
        pass
