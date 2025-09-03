"""
Abstract Base Classes and Interfaces for xnode library.

This module defines the core interfaces that ensure consistency,
extensibility, and maintainability across the xnode library.
"""

import sys
from abc import ABC, abstractmethod
from typing import Any, Iterator, Union, Optional, Callable, Protocol, runtime_checkable

# B4: For Python < 3.8, Protocol must be imported from typing_extensions.
# This ensures backward compatibility for projects using older Python versions.
if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol

# Import custom exceptions to be used in docstrings
from .errors import (
    xNodePathError,
    xNodeTypeError,
    xNodeValueError
)


# ============================================================================
# CORE NODE INTERFACES
# ============================================================================

class iNode(ABC):
    """
    Core interface for all nodes in the xnode tree.

    This interface defines the fundamental operations that all nodes
    must support, ensuring consistency across different node types.
    These methods are considered internal-facing, to be called by the
    public facade, hence the underscore prefix.
    """

    @property
    @abstractmethod
    def parent(self) -> Optional['iNode']:
        """Get the parent node."""
        pass

    @parent.setter
    @abstractmethod
    def parent(self, value: Optional['iNode']) -> None:
        """Set the parent node."""
        pass

    @abstractmethod
    def _get_child(self, key_or_index: Union[str, int]) -> 'iNode':
        """
        Get a child node by key or index.

        :raises KeyError: If the key does not exist in a dictionary-like node.
        :raises IndexError: If the index is out of range in a list-like node.
        """
        pass

    @abstractmethod
    def _to_native(self) -> Any:
        """Convert this node and its children to a native Python object."""
        pass

    @abstractmethod
    def _get_root(self) -> 'iNode':
        """Get the root node of the tree."""
        pass

    @abstractmethod
    def _get_path(self) -> str:
        """Get the path from the root to this node as a dot-separated string."""
        pass


class iNodeValue(iNode):
    """
    Interface for leaf nodes that contain primitive values.

    Leaf nodes are the terminal nodes in the tree that contain
    actual data values rather than other nodes.
    """

    @property
    @abstractmethod
    def value(self) -> Any:
        """Get the primitive value stored in this leaf node."""
        pass


class iNodeContainer(iNode):
    """
    Interface for container nodes that can hold other nodes.

    Container nodes (lists, dicts) can have children and support
    iteration and access operations.
    """

    @abstractmethod
    def __len__(self) -> int:
        """Get the number of children in this container."""
        pass

    @abstractmethod
    def __iter__(self) -> Iterator['iNode']:
        """Iterate over child nodes."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Remove all children from this container."""
        pass

    @abstractmethod
    def contains(self, node: 'iNode') -> bool:
        """Check if this container contains the given node."""
        pass

    @abstractmethod
    def copy(self) -> 'iNodeContainer':
        """Create a shallow copy of this container."""
        pass


class iNodeList(iNodeContainer):
    """Interface for list-like nodes that support indexed access."""

    @abstractmethod
    def append(self, node: 'iNode') -> None:
        """Append a child node to this list."""
        pass

    @abstractmethod
    def insert(self, index: int, node: 'iNode') -> None:
        """
        Insert a child node at the specified index.
        :raises IndexError: If the index is out of range.
        """
        pass

    @abstractmethod
    def remove(self, node: 'iNode') -> None:
        """
        Remove a specific node from the list.
        :raises xNodeValueError: If the node is not present in the list.
        """
        pass

    @abstractmethod
    def pop(self, index: int = -1) -> 'iNode':
        """
        Remove and return node at the given index (default last).
        :raises IndexError: If the index is out of range.
        """
        pass

    @abstractmethod
    def extend(self, nodes: Iterator['iNode']) -> None:
        """Extend list with multiple nodes from an iterator."""
        pass

    @abstractmethod
    def reverse(self) -> None:
        """Reverse the order of nodes in the list in-place."""
        pass

    @abstractmethod
    def sort(self, key: Optional[Callable] = None) -> None:
        """Sort nodes in the list in-place."""
        pass


class iNodeDict(iNodeContainer):
    """Interface for dictionary-like nodes that support key-based access."""

    @abstractmethod
    def set_child(self, key: str, node: 'iNode') -> None:
        """Set a child node with the specified key."""
        pass

    @abstractmethod
    def keys(self) -> Iterator[str]:
        """Get an iterator over the keys of this dictionary."""
        pass

    @abstractmethod
    def items(self) -> Iterator[tuple[str, 'iNode']]:
        """Get an iterator over key-node pairs."""
        pass

    @abstractmethod
    def remove_child(self, key: str) -> Optional['iNode']:
        """
        Remove and return child node by key. Returns None if key not found.
        """
        pass

    @abstractmethod
    def has_key(self, key: str) -> bool:
        """Check if a key exists in this dictionary."""
        pass

    @abstractmethod
    def values(self) -> Iterator['iNode']:
        """Get an iterator over the child nodes (values)."""
        pass

    @abstractmethod
    def update(self, other: 'iNodeDict') -> None:
        """Update this dict with items from another dict node."""
        pass

    @abstractmethod
    def get_child(self, key: str, default: Any = None) -> Optional['iNode']:
        """Get a child node by key, returning a default value if not found."""
        pass


class iNodeReference(iNode):
    """Interface for reference nodes that point to external resources."""

    @property
    @abstractmethod
    def uri(self) -> str:
        """Get the URI/path/identifier that this reference points to."""
        pass

    @property
    @abstractmethod
    def reference_type(self) -> str:
        """Get the type of reference (e.g., 'url', 'path', 'id', 'generic')."""
        pass

    @property
    @abstractmethod
    def metadata(self) -> dict[str, Any]:
        """Get metadata about the reference."""
        pass


class iNodeObject(iNode):
    """Interface for object nodes that reference external objects like files."""

    @property
    @abstractmethod
    def uri(self) -> str:
        """Get the URI/path where the object is located."""
        pass

    @property
    @abstractmethod
    def object_type(self) -> str:
        """Get the type of object (e.g., 'image', 'video', 'audio', 'document')."""
        pass

    @property
    @abstractmethod
    def mime_type(self) -> Optional[str]:
        """Get the MIME type of the object."""
        pass

    @property
    @abstractmethod
    def size(self) -> Optional[int]:
        """Get the size of the object in bytes."""
        pass

    @property
    @abstractmethod
    def metadata(self) -> dict[str, Any]:
        """Get metadata about the object."""
        pass


# ============================================================================
# PUBLIC FACADE INTERFACES
# ============================================================================

class iNodeFacade(ABC):
    """
    Public interface for the Node Facade.

    This interface defines the public API that users interact with,
    providing a clean, immutable-feeling view of the underlying node tree.
    """

    # Factory Methods
    @staticmethod
    @abstractmethod
    def from_native(data: Any) -> 'iNodeFacade':
        """
        Create a new Node tree from a native Python object.

        .. warning::
            B8: Deserializing data from untrusted sources can be a security risk.
            Always validate or sanitize input data.
        """
        pass

    @staticmethod
    @abstractmethod
    def create_reference(
        uri: str,
        reference_type: str = "generic",
        metadata: Optional[dict[str, Any]] = None
    ) -> 'iNodeFacade':
        """Create a new Node containing a reference."""
        pass

    @staticmethod
    @abstractmethod
    def create_object(
        uri: str,
        object_type: str,
        mime_type: Optional[str] = None,
        size: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> 'iNodeFacade':
        """Create a new Node containing an object reference."""
        pass

    # Properties
    @property
    @abstractmethod
    def value(self) -> Any:
        """Get the value of this node."""
        pass

    @property
    @abstractmethod
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        pass

    @property
    @abstractmethod
    def is_list(self) -> bool:
        """Check if this is a list node."""
        pass

    @property
    @abstractmethod
    def is_dict(self) -> bool:
        """Check if this is a dictionary node."""
        pass

    @property
    @abstractmethod
    def is_reference(self) -> bool:
        """Check if this is a reference node."""
        pass

    @property
    @abstractmethod
    def is_object(self) -> bool:
        """Check if this is an object node."""
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        """Get the type of this node as a string (e.g., 'list', 'dict', 'leaf')."""
        pass

    # Reference/Object Properties
    @property
    @abstractmethod
    def uri(self) -> Optional[str]:
        """Get the URI for reference or object nodes, otherwise None."""
        pass

    @property
    @abstractmethod
    def reference_type(self) -> Optional[str]:
        """Get the reference type for reference nodes, otherwise None."""
        pass

    @property
    @abstractmethod
    def object_type(self) -> Optional[str]:
        """Get the object type for object nodes, otherwise None."""
        pass

    @property
    @abstractmethod
    def mime_type(self) -> Optional[str]:
        """Get the MIME type for object nodes, otherwise None."""
        pass

    @property
    @abstractmethod
    def size(self) -> Optional[int]:
        """Get the size for object nodes, otherwise None."""
        pass

    @property
    @abstractmethod
    def metadata(self) -> Optional[dict[str, Any]]:
        """Get metadata for reference or object nodes, otherwise None."""
        pass

    # Navigation Methods
    @abstractmethod
    def find(self, path: str) -> 'iNodeFacade':
        """
        Find a node using a dot-separated path.

        :raises xNodePathError: If the path is not found.
        """
        pass

    @abstractmethod
    def get(self, path: str, default: Any = None) -> Optional['iNodeFacade']:
        """Get a node using a path, returning a default value if not found."""
        pass

    @abstractmethod
    def __getitem__(self, key_or_index: Union[str, int]) -> 'iNodeFacade':
        """
        Get a child node using bracket notation.

        :raises xNodePathError: If the key does not exist.
        :raises IndexError: If the index is out of range.
        :raises xNodeTypeError: If the node is not a container.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Get the number of children in this node."""
        pass

    @abstractmethod
    def __iter__(self) -> Iterator['iNodeFacade']:
        """Iterate over child nodes."""
        pass

    @abstractmethod
    def keys(self) -> Iterator[str]:
        """
        Get keys for dictionary nodes.

        :raises xNodeTypeError: If the node is not a dictionary-like node.
        """
        pass

    @abstractmethod
    def items(self) -> Iterator[tuple[str, 'iNodeFacade']]:
        """
        Get key-value pairs for dictionary nodes.

        :raises xNodeTypeError: If the node is not a dictionary-like node.
        """
        pass

    # Conversion Methods
    @abstractmethod
    def to_native(self) -> Any:
        """Convert this node tree to a native Python object."""
        pass

    # String Representation
    @abstractmethod
    def __repr__(self) -> str:
        """Get a developer-friendly string representation of this node."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Get a user-friendly string representation of this node."""
        pass

    # Utility Methods
    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if a path exists in the tree."""
        pass

    @abstractmethod
    def count(self, path: str = ".") -> int:
        """Count nodes at the given path."""
        pass

    @abstractmethod
    def flatten(self, separator: str = ".") -> dict[str, Any]:
        """Flatten the tree into a single-level dictionary of path-value pairs."""
        pass

    @abstractmethod
    def merge(self, other: 'iNodeFacade', strategy: str = "replace") -> 'iNodeFacade':
        """Merge with another node tree, returning a new tree."""
        pass

    @abstractmethod
    def diff(self, other: 'iNodeFacade') -> dict[str, Any]:
        """Get the differences between this and another node tree."""
        pass

    @abstractmethod
    def transform(self, transformer: Callable) -> 'iNodeFacade':
        """Apply a transformation function to all nodes, returning a new tree."""
        pass

    @abstractmethod
    def select(self, *paths: str) -> dict[str, 'iNodeFacade']:
        """Select multiple nodes by their paths in a single operation."""
        pass


# ============================================================================
# FACTORY INTERFACES
# ============================================================================

class iNodeFactory(ABC):
    """
    Interface for a node factory that creates different types of nodes.

    The factory pattern ensures consistent node creation and allows
    for easy extension with new node types.
    """

    @staticmethod
    @abstractmethod
    def from_native(data: Any, parent: Optional[iNode] = None) -> iNode:
        """
        Create a node from a native Python object.

        .. warning::
            B8: Deserializing data from untrusted sources can be a security risk.
            Ensure data is validated.
        """
        pass

    @staticmethod
    @abstractmethod
    def to_native(node: iNode) -> Any:
        """Convert a node back to a native Python object."""
        pass

    @staticmethod
    @abstractmethod
    def create_reference(
        uri: str,
        reference_type: str = "generic",
        metadata: Optional[dict[str, Any]] = None,
        parent: Optional[iNode] = None
    ) -> iNodeReference:
        """Create a reference node."""
        pass

    @staticmethod
    @abstractmethod
    def create_object(
        uri: str,
        object_type: str,
        mime_type: Optional[str] = None,
        size: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None,
        parent: Optional[iNode] = None
    ) -> iNodeObject:
        """Create an object node."""
        pass


# ============================================================================
# PROTOCOL INTERFACES (Runtime Checkable)
# ============================================================================

@runtime_checkable
class iNodeProtocol(Protocol):
    """
    Protocol for internal nodes that can be checked at runtime.

    This allows for duck typing and runtime type checking of node implementations
    without requiring explicit inheritance from iNode.
    """

    parent: Optional['iNodeProtocol']

    def _get_child(self, key_or_index: Union[str, int]) -> 'iNodeProtocol': ...
    def _to_native(self) -> Any: ...
    def _get_root(self) -> 'iNodeProtocol': ...
    def _get_path(self) -> str: ...


@runtime_checkable
class iNodeFacadeProtocol(Protocol):
    """Protocol for the public Node Facade that can be checked at runtime."""

    value: Any
    is_leaf: bool
    is_list: bool
    is_dict: bool
    is_reference: bool
    is_object: bool
    type: str

    def find(self, path: str) -> 'iNodeFacadeProtocol': ...
    def get(self, path: str, default: Any = None) -> Optional['iNodeFacadeProtocol']: ...
    def __getitem__(self, key_or_index: Union[str, int]) -> 'iNodeFacadeProtocol': ...
    def to_native(self) -> Any: ...


# ============================================================================
# PERFORMANCE INTERFACES
# ============================================================================

class iPerformanceOptimized(ABC):
    """
    Interface for performance-optimized implementations.

    This interface defines methods that implementations can use
    to optimize performance-critical operations.
    """

    @abstractmethod
    def _optimize_for_access(self) -> None:
        """Optimize the node for fast key/index-based access operations."""
        pass

    @abstractmethod
    def _optimize_for_iteration(self) -> None:
        """Optimize the node for fast iteration operations."""
        pass

    @abstractmethod
    def _cache_path(self, path: str, node: 'iNode') -> None:
        """Cache a path lookup for faster future access."""
        pass

    @abstractmethod
    def _clear_cache(self) -> None:
        """Clear any cached data."""
        pass

    @abstractmethod
    def _get_memory_usage(self) -> int:
        """Get current memory usage of the node and its children in bytes."""
        pass

    @abstractmethod
    def _optimize_memory(self) -> None:
        """Attempt to optimize the memory footprint of the node tree."""
        pass

    @abstractmethod
    def _get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics, such as cache hits/misses."""
        pass


# ============================================================================
# EXTENSIBILITY INTERFACES
# ============================================================================

class iExtensible(ABC):
    """
    Interface for extensible implementations.

    This interface allows for plugin-like extensions and
    custom behavior without modifying core code.
    """

    @abstractmethod
    def register_extension(self, name: str, extension: Any) -> None:
        """Register an extension with the given name."""
        pass

    @abstractmethod
    def get_extension(self, name: str) -> Optional[Any]:
        """Get an extension by name, returning None if not found."""
        pass

    @abstractmethod
    def has_extension(self, name: str) -> bool:
        """Check if an extension is registered."""
        pass

    @abstractmethod
    def list_extensions(self) -> list[str]:
        """List all registered extension names."""
        pass

    @abstractmethod
    def remove_extension(self, name: str) -> bool:
        """Remove an extension by name. Returns True if successful."""
        pass

    @abstractmethod
    def has_extension_type(self, extension_type: str) -> bool:
        """Check if any extension of a given type is registered."""
        pass


class iNodeCustom(iNode, iExtensible):
    """
    Interface for custom node implementations.

    This interface allows users to create their own node types
    while maintaining compatibility with the xnode system.
    """

    @abstractmethod
    def get_custom_type(self) -> str:
        """Get the custom type identifier for this node."""
        pass

    @abstractmethod
    def get_custom_data(self) -> Any:
        """Get the custom data stored in this node."""
        pass

    @abstractmethod
    def set_custom_data(self, data: Any) -> None:
        """Set the custom data for this node."""
        pass


# ============================================================================
# VALIDATION INTERFACES
# ============================================================================

class iValidatable(ABC):
    """Interface for nodes that support validation."""

    @abstractmethod
    def validate(self) -> bool:
        """Validate the node and its children against internal rules."""
        pass

    @abstractmethod
    def get_validation_errors(self) -> list[str]:
        """Get a list of validation errors."""
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        """Check if the node is valid."""
        pass

    @abstractmethod
    def validate_schema(self, schema: Any) -> bool:
        """Validate the node tree against a specific external schema."""
        pass

    @abstractmethod
    def get_validation_warnings(self) -> list[str]:
        """Get validation warnings (non-critical issues)."""
        pass

    @abstractmethod
    def fix_validation_errors(self) -> bool:
        """Attempt to fix validation errors automatically. Returns True if successful."""
        pass


# ============================================================================
# SERIALIZATION INTERFACES
# ============================================================================

class iSerializable(ABC):
    """Interface for nodes that support custom serialization."""

    @abstractmethod
    def serialize(self, format: str = "native") -> Any:
        """Serialize the node to the specified format (e.g., 'native', 'custom')."""
        pass

    @abstractmethod
    def deserialize(self, data: Any, format: str = "native") -> None:
        """
        Deserialize data in the specified format into this node.

        .. warning::
            B8: Deserializing data from untrusted sources can be a security risk.
            Always validate or sanitize input data.
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        """Get a list of supported serialization formats."""
        pass

    @abstractmethod
    def to_file(self, path: str, format: str = "auto") -> None:
        """Serialize the node tree to a file."""
        pass

    @abstractmethod
    def from_file(self, path: str, format: str = "auto") -> None:
        """
        Deserialize data from a file into this node.

        .. warning::
            B8: Deserializing data from untrusted files can be a security risk.
            Ensure the source is trusted.
        """
        pass

    @abstractmethod
    def get_format_from_extension(self, extension: str) -> Optional[str]:
        """Attempt to guess the format from a file extension."""
        pass


# ============================================================================
# EXPORT ALL INTERFACES
# ============================================================================

__all__ = [
    # Core Node Interfaces
    'iNode',
    'iNodeValue',
    'iNodeContainer',
    'iNodeList',
    'iNodeDict',
    'iNodeReference',
    'iNodeObject',

    # Public Facade Interfaces
    'iNodeFacade',

    # Factory Interfaces
    'iNodeFactory',

    # Protocol Interfaces
    'iNodeProtocol',
    'iNodeFacadeProtocol',

    # Performance Interfaces
    'iPerformanceOptimized',

    # Extensibility Interfaces
    'iExtensible',
    'iNodeCustom',

    # Validation Interfaces
    'iValidatable',

    # Serialization Interfaces
    'iSerializable',
]
