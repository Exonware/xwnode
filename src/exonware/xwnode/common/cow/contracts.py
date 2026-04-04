#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/common/cow/contracts.py
COW Contracts - Interfaces for Copy-on-Write Components
Defines the contracts for immutable data structures with structural sharing.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.21
Generation Date: 26-Oct-2025
"""

from __future__ import annotations
from collections.abc import Iterator
from typing import Any, Protocol, runtime_checkable
@runtime_checkable

class ICOWNode(Protocol):
    """
    Interface for Copy-on-Write nodes.
    Provides immutable operations with structural sharing for
    optimal performance and memory efficiency.
    """

    def get(self, path: str, default: Any = None) -> Any:
        """
        Get value at path.
        Args:
            path: Dot-separated path to value
            default: Default value if path doesn't exist
        Returns:
            Value at path or default
        Time Complexity: O(log n) with HAMT
        """
        ...

    def set(self, path: str, value: Any) -> ICOWNode:
        """
        Set value at path, returning new node (COW).
        Args:
            path: Dot-separated path to set
            value: Value to set
        Returns:
            New ICOWNode with updated value (original unchanged)
        Time Complexity: O(log n) with structural sharing
        """
        ...

    def delete(self, path: str) -> ICOWNode:
        """
        Delete path, returning new node (COW).
        Args:
            path: Path to delete
        Returns:
            New ICOWNode without the path (original unchanged)
        Time Complexity: O(log n)
        """
        ...

    def to_native(self) -> Any:
        """
        Convert to native Python data.
        Returns:
            Native Python dict/list/value
        Time Complexity: O(n) - must reconstruct
        """
        ...

    def exists(self, path: str) -> bool:
        """
        Check if path exists.
        Args:
            path: Path to check
        Returns:
            True if path exists, False otherwise
        Time Complexity: O(log n)
        """
        ...

    def get_version(self) -> int:
        """
        Get node version for cache invalidation.
        Returns:
            Version number (increments on mutation)
        """
        ...

    def __len__(self) -> int:
        """
        Get number of paths in node.
        Returns:
            Path count
        """
        ...

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over paths.
        Yields:
            Path strings
        """
        ...
@runtime_checkable

class ICOWStrategy(Protocol):
    """
    Interface for COW strategy implementations.
    Different strategies (HAMT, path-based, etc.) can implement
    this interface for optimal performance with different data types.
    """

    def get_value(self, path: str, default: Any = None) -> Any:
        """
        Get value at path.
        Args:
            path: Path to get
            default: Default if not found
        Returns:
            Value or default
        """
        ...

    def set_value(self, path: str, value: Any) -> ICOWStrategy:
        """
        Set value, returning new strategy instance (COW).
        Args:
            path: Path to set
            value: Value to set
        Returns:
            New strategy with updated value
        """
        ...

    def delete_value(self, path: str) -> ICOWStrategy:
        """
        Delete path, returning new strategy instance (COW).
        Args:
            path: Path to delete
        Returns:
            New strategy without path
        """
        ...

    def has_path(self, path: str) -> bool:
        """
        Check if path exists.
        Args:
            path: Path to check
        Returns:
            True if exists
        """
        ...

    def get_paths(self) -> dict[str, Any]:
        """
        Get all paths and values.
        Returns:
            Dictionary of path -> value mappings
        """
        ...

    def get_version(self) -> int:
        """
        Get strategy version.
        Returns:
            Version number
        """
        ...
