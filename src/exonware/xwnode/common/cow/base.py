#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/common/cow/base.py
COW Base Classes - Abstract Implementations
Provides base implementations for Copy-on-Write components.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.14
Generation Date: 26-Oct-2025
"""

from __future__ import annotations
from collections.abc import Iterator
from abc import abstractmethod
from typing import Any
from .contracts import ICOWNode, ICOWStrategy


class ACOWNode(ICOWNode):
    """
    Abstract base class for COW nodes.
    Provides common functionality for immutable node operations.
    """

    def __init__(self, strategy: ICOWStrategy):
        """
        Initialize with a COW strategy.
        Args:
            strategy: COW strategy implementation
        """
        self._strategy = strategy

    def get(self, path: str, default: Any = None) -> Any:
        """Get value at path using strategy."""
        return self._strategy.get_value(path, default)

    def set(self, path: str, value: Any) -> ACOWNode:
        """Set value, returning new node with updated strategy."""
        new_strategy = self._strategy.set_value(path, value)
        return self.__class__(new_strategy)

    def delete(self, path: str) -> ACOWNode:
        """Delete path, returning new node."""
        new_strategy = self._strategy.delete_value(path)
        return self.__class__(new_strategy)

    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self._strategy.has_path(path)

    def to_native(self) -> Any:
        """Convert to native Python data."""
        paths = self._strategy.get_paths()
        return self._reconstruct_native(paths)

    def get_version(self) -> int:
        """Get node version."""
        return self._strategy.get_version()

    def __len__(self) -> int:
        """Get number of paths."""
        return len(self._strategy.get_paths())

    def __iter__(self) -> Iterator[str]:
        """Iterate over paths."""
        return iter(self._strategy.get_paths().keys())
    @staticmethod

    def _reconstruct_native(paths: dict[str, Any]) -> Any:
        """
        Reconstruct native Python data from flat paths.
        Args:
            paths: Dictionary of path -> value mappings
        Returns:
            Reconstructed native Python data (dict/list/value)
        """
        if not paths:
            return {}
        # Determine root type from paths
        has_numeric_keys = any(path.split('.')[0].isdigit() for path in paths if path)
        root = [] if has_numeric_keys else {}
        for path, value in paths.items():
            if not path:
                # Root value
                return value
            parts = path.split('.')
            current = root
            # Stack of (parent, key) where parent[key] is current (so we can replace list with dict)
            stack: list[tuple[Any, Any]] = []
            # Navigate to parent
            for i, part in enumerate(parts[:-1]):
                if isinstance(current, dict):
                    if part not in current:
                        # Determine type for next level (use list only for 0-based indices, not keys like "200"/"404")
                        next_part = parts[i + 1]
                        next_is_array_index = (
                            next_part.isdigit()
                            and (next_part == "0" or int(next_part) < 100)
                        )
                        current[part] = [] if next_is_array_index else {}
                    stack.append((current, part))
                    current = current[part]
                elif isinstance(current, list):
                    if not part.isdigit():
                        # Non-digit key (e.g. "default") — convert this list to dict so we can use string keys
                        if stack:
                            parent, key = stack[-1]
                            parent[key] = {str(j): current[j] for j in range(len(current))}
                            current = parent[key]
                            if part not in current:
                                next_part = parts[i + 1]
                                next_is_array_index = (
                                    next_part.isdigit()
                                    and (next_part == "0" or int(next_part) < 100)
                                )
                                current[part] = [] if next_is_array_index else {}
                            stack.append((current, part))
                            current = current[part]
                        else:
                            # Root was list; replace with dict
                            root = {str(j): current[j] for j in range(len(current))}
                            current = root
                            if part not in current:
                                next_part = parts[i + 1]
                                next_is_array_index = (
                                    next_part.isdigit()
                                    and (next_part == "0" or int(next_part) < 100)
                                )
                                current[part] = [] if next_is_array_index else {}
                            stack.append((current, part))
                            current = current[part]
                    else:
                        idx = int(part)
                        while len(current) <= idx:
                            current.append(None)
                        if current[idx] is None:
                            next_part = parts[i + 1]
                            next_is_array_index = (
                                next_part.isdigit()
                                and (next_part == "0" or int(next_part) < 100)
                            )
                            current[idx] = [] if next_is_array_index else {}
                        stack.append((current, idx))
                        current = current[idx]
            # Set final value
            final_key = parts[-1]
            if isinstance(current, dict):
                current[final_key] = value
            elif isinstance(current, list):
                if not final_key.isdigit():
                    if stack:
                        parent, key = stack[-1]
                        parent[key] = {str(j): current[j] for j in range(len(current))}
                        current = parent[key]
                        current[final_key] = value
                    else:
                        root = {str(j): current[j] for j in range(len(current))}
                        root[final_key] = value
                else:
                    idx = int(final_key)
                    while len(current) <= idx:
                        current.append(None)
                    current[idx] = value
        return root


class ACOWStrategy(ICOWStrategy):
    """
    Abstract base class for COW strategies.
    Provides common functionality for different COW implementations.
    """

    def __init__(self, paths: dict[str, Any] | None = None, version: int = 0):
        """
        Initialize with paths and version.
        Args:
            paths: Path -> value mappings
            version: Version number for cache invalidation
        """
        self._paths = paths if paths is not None else {}
        self._version = version

    def get_value(self, path: str, default: Any = None) -> Any:
        """Get value at path."""
        return self._paths.get(path, default)

    def has_path(self, path: str) -> bool:
        """Check if path exists."""
        return path in self._paths

    def get_paths(self) -> dict[str, Any]:
        """Get all paths."""
        return self._paths

    def get_version(self) -> int:
        """Get version number."""
        return self._version
    @abstractmethod

    def set_value(self, path: str, value: Any) -> ACOWStrategy:
        """
        Set value (must be implemented by subclass).
        Subclasses implement different strategies:
        - HAMT: Tree-based with structural sharing
        - Path-based: Simple dict copy
        - Optimized: Strategy-specific implementations
        """
        pass
    @abstractmethod

    def delete_value(self, path: str) -> ACOWStrategy:
        """Delete value (must be implemented by subclass)."""
        pass
