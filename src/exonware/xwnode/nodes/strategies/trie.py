#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/trie.py
Trie Node Strategy Implementation
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.6
Generation Date: 16-Jan-2026
"""

from __future__ import annotations
from collections.abc import AsyncIterator, Iterator
"""
Trie Node Strategy Implementation
This module implements the TRIE strategy for efficient string prefix operations.
"""
from typing import Any
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait
from ...errors import XWNodeUnsupportedCapabilityError


class TrieNode:
    """Node in the trie structure."""

    def __init__(self):
        """Time Complexity: O(1)"""
        self.children: dict[str, TrieNode] = {}
        self.is_end_of_word = False
        self.value: Any = None


class TrieStrategy(ANodeTreeStrategy):
    """
    Trie (Prefix Tree) strategy for efficient prefix-based string operations.
    WHY Trie:
    - O(k) operations where k = key length (independent of dataset size)
    - Exceptional prefix matching and autocomplete
    - Natural string organization by shared prefixes
    - Memory-efficient for datasets with common prefixes
    WHY this implementation:
    - Standard trie algorithm with character-by-character nodes
    - Dictionary-based children for flexible character sets
    - End-of-word markers for distinguishing prefixes from complete words
    - Supports full Unicode character set
    Time Complexity:
    - Insert: O(k) where k = key length
    - Search: O(k) - traverse k characters
    - Delete: O(k) - traverse and cleanup
    - Prefix search: O(k + m) where m = matching words
    - Autocomplete: O(k + m) where m = suggestions
    Space Complexity: O(ALPHABET_SIZE * N * K) worst case, often much better
    Trade-offs:
    - Advantage: Time independent of dataset size
    - Advantage: Natural prefix operations
    - Advantage: Memory sharing for common prefixes
    - Limitation: Higher memory than hash for unique keys
    - Compared to Hash Map: Slower exact match, better for prefixes
    Best for:
    - Autocomplete systems
    - Dictionary/spell check
    - IP routing tables
    - String prefix matching
    Not recommended for:
    - Non-string keys (use HASH_MAP)
    - Exact match only (use HASH_MAP)
    - Numeric keys (use B_TREE)
    Following eXonware Priorities:
    1. Security: Bounded by key length
    2. Usability: Intuitive for string operations
    3. Maintainability: Well-known algorithm
    4. Performance: O(k) guaranteed
    5. Extensibility: Can add compression (Radix)
    """
    # Strategy type classification
    STRATEGY_TYPE = NodeType.TREE

    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize the trie strategy.
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        super().__init__(NodeMode.TRIE, traits, **options)
        self._root = TrieNode()
        self._size = 0

    def get_supported_traits(self) -> NodeTrait:
        """
        Get the traits supported by the trie strategy.
        Time Complexity: O(1)
        """
        return (NodeTrait.ORDERED | NodeTrait.HIERARCHICAL | NodeTrait.INDEXED)
    # ============================================================================
    # CORE OPERATIONS
    # ============================================================================

    def insert(self, key: Any, value: Any) -> None:
        """
        Store a key-value pair (key should be string-like).
        Time Complexity: O(k) where k is key length
        Space Complexity: O(k) in worst case for new branches
        """
        word = str(key)
        node = self._root
        # Traverse/create path
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        # Mark end of word and store value
        if not node.is_end_of_word:
            self._size += 1
        node.is_end_of_word = True
        node.value = value

    def find(self, key: Any) -> Any:
        """
        Retrieve a value by key.
        Time Complexity: O(k) where k is key length
        """
        word = str(key)
        node = self._root
        # Traverse path
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return node.value if node.is_end_of_word else None

    def delete(self, key: Any) -> bool:
        """
        Remove a key-value pair.
        Time Complexity: O(k) where k is key length
        """
        word = str(key)
        return self._delete_helper(self._root, word, 0)

    def _delete_helper(self, node: TrieNode, word: str, index: int) -> bool:
        """
        Helper method for deletion.
        Time Complexity: O(k) where k is key length
        """
        if index == len(word):
            if node.is_end_of_word:
                node.is_end_of_word = False
                node.value = None
                self._size -= 1
                return True
            return False
        char = word[index]
        if char not in node.children:
            return False
        deleted = self._delete_helper(node.children[char], word, index + 1)
        # Clean up empty nodes
        if deleted and not node.children[char].children and not node.children[char].is_end_of_word:
            del node.children[char]
        return deleted

    def size(self) -> int:
        """
        Get the number of items.
        Time Complexity: O(1)
        """
        return self._size

    def is_empty(self) -> bool:
        """
        Check if the structure is empty.
        Time Complexity: O(1)
        """
        return self._size == 0

    def to_native(self) -> dict[str, Any]:
        """
        Convert to native Python dictionary.
        Time Complexity: O(n * k) where n is words, k is average key length
        """
        result = {}
        self._collect_words(self._root, "", result)
        return result
    # ============================================================================
    # ASYNC API - Lightweight wrappers (NO lock overhead, v0.0.1.28b)
    # ============================================================================

    async def insert_async(self, key: Any, value: Any) -> None:
        """Lightweight async wrapper for insert (no lock overhead)."""
        return self.insert(key, value)

    async def find_async(self, key: Any) -> Any | None:
        """Lightweight async wrapper for find (no lock overhead)."""
        return self.find(key)

    async def delete_async(self, key: Any) -> bool:
        """Lightweight async wrapper for delete (no lock overhead)."""
        return self.delete(key)

    async def size_async(self) -> int:
        """Lightweight async wrapper for size (no lock overhead)."""
        return self.size()

    async def is_empty_async(self) -> bool:
        """Lightweight async wrapper for is_empty (no lock overhead)."""
        return self.is_empty()

    async def to_native_async(self) -> Any:
        """Lightweight async wrapper for to_native (no lock overhead)."""
        return self.to_native()

    async def keys_async(self) -> AsyncIterator[Any]:
        """Lightweight async wrapper for keys (no lock overhead)."""
        for key in self.keys():
            yield key

    async def values_async(self) -> AsyncIterator[Any]:
        """Lightweight async wrapper for values (no lock overhead)."""
        for value in self.values():
            yield value

    async def items_async(self) -> AsyncIterator[tuple[Any, Any]]:
        """Lightweight async wrapper for items (no lock overhead)."""
        for item in self.items():
            yield item

    def _collect_words(self, node: TrieNode, prefix: str, result: dict[str, Any]) -> None:
        """Collect all words from trie."""
        if node.is_end_of_word:
            result[prefix] = node.value
        for char, child in node.children.items():
            self._collect_words(child, prefix + char, result)
    # ============================================================================
    # TREE STRATEGY METHODS
    # ============================================================================

    def traverse(self, order: str = 'inorder') -> list[Any]:
        """Traverse tree in specified order."""
        result = []
        self._collect_words(self._root, "", result)
        return list(result.values())

    def get_min(self) -> Any:
        """Get minimum key."""
        # Find leftmost word
        node = self._root
        word = ""
        while node.children:
            char = min(node.children.keys())
            word += char
            node = node.children[char]
        return word if node.is_end_of_word else None

    def get_max(self) -> Any:
        """Get maximum key."""
        # Find rightmost word
        node = self._root
        word = ""
        while node.children:
            char = max(node.children.keys())
            word += char
            node = node.children[char]
        return word if node.is_end_of_word else None
    # ============================================================================
    # AUTO-3 Phase 2 methods
    # ============================================================================

    def as_trie(self):
        """Provide Trie behavioral view."""
        return self

    def as_heap(self):
        """
        Provide Heap behavioral view.
        Trie cannot meaningfully behave as a heap (different data structure).
        Raises NotImplementedError to indicate incompatibility.
        """
        raise NotImplementedError(
            "Trie cannot behave as Heap - use HeapStrategy for priority-based operations"
        )

    def as_skip_list(self):
        """
        Provide SkipList behavioral view.
        Trie cannot meaningfully behave as a skip list (different data structure).
        Raises NotImplementedError to indicate incompatibility.
        """
        raise NotImplementedError(
            "Trie cannot behave as SkipList - use SkipListStrategy for probabilistic sorted operations"
        )
    # ============================================================================
    # TRIE SPECIFIC OPERATIONS
    # ============================================================================

    def prefix_search(self, prefix: str) -> list[str]:
        """Find all keys with given prefix."""
        node = self._root
        # Navigate to prefix
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        # Collect all words with this prefix
        result = []
        self._collect_words(node, prefix, result)
        return list(result.keys())

    def longest_common_prefix(self) -> str:
        """Find longest common prefix of all keys."""
        if not self._root.children:
            return ""
        prefix = ""
        node = self._root
        while len(node.children) == 1 and not node.is_end_of_word:
            char = list(node.children.keys())[0]
            prefix += char
            node = node.children[char]
        return prefix

    def keys_with_prefix(self, prefix: str) -> list[str]:
        """Get all keys with given prefix."""
        return self.prefix_search(prefix)

    def keys_with_suffix(self, suffix: str) -> list[str]:
        """
        Get all keys with given suffix.
        Implements suffix search by traversing the trie and checking if keys end with suffix.
        Time Complexity: O(n * m) where n is number of keys, m is suffix length
        """
        if not suffix:
            return list(self.keys())
        result = []
        # Collect all keys and filter by suffix
        for key in self.keys():
            if key.endswith(suffix):
                result.append(key)
        return result
    # ============================================================================
    # ITERATION
    # ============================================================================

    def keys(self) -> Iterator[str]:
        """Get all keys."""
        result = {}
        self._collect_words(self._root, "", result)
        return iter(result.keys())

    def values(self) -> Iterator[Any]:
        """Get all values."""
        result = {}
        self._collect_words(self._root, "", result)
        return iter(result.values())

    def items(self) -> Iterator[tuple[str, Any]]:
        """Get all key-value pairs."""
        result = {}
        self._collect_words(self._root, "", result)
        return iter(result.items())
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    @property

    def backend_info(self) -> dict[str, Any]:
        """Get backend implementation info."""
        return {
            'strategy': 'TRIE',
            'backend': 'Trie tree',
            'complexity': {
                'insert': 'O(m)',
                'search': 'O(m)',
                'delete': 'O(m)',
                'prefix_search': 'O(m + k)',
                'space': 'O(ALPHABET_SIZE * N * M)'
            }
        }
    @property

    def metrics(self) -> dict[str, Any]:
        """Get performance metrics."""
        return {
            'size': self._size,
            'memory_usage': f"{self._size * 32} bytes (estimated)",
            'height': self._get_height()
        }

    def _get_height(self) -> int:
        """Get height of trie."""
        return self._height_helper(self._root)

    def _height_helper(self, node: TrieNode) -> int:
        """Helper for height calculation."""
        if not node.children:
            return 0
        return 1 + max(self._height_helper(child) for child in node.children.values())
    # ============================================================================
    # REQUIRED INTERFACE METHODS (iNodeStrategy)
    # ============================================================================

    def create_from_data(self, data: Any) -> TrieStrategy:
        """Create strategy instance from data."""
        new_strategy = TrieStrategy(self._traits)
        if isinstance(data, dict):
            for key, value in data.items():
                new_strategy.insert(key, value)
        elif isinstance(data, list):
            for item in data:
                new_strategy.insert(item, item)
        return new_strategy

    def get(self, path: str, default: Any = None) -> Any:
        """Get value by path (trie uses find)."""
        result = self.find(path)
        return result if result is not None else default

    def has(self, key: Any) -> bool:
        """Check if key exists."""
        return self.find(str(key)) is not None

    def put(self, path: str, value: Any) -> TrieStrategy:
        """Put value at path."""
        self.insert(path, value)
        return self

    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self.find(path) is not None
    # Container protocol

    def __len__(self) -> int:
        """Get length."""
        return self._size

    def __iter__(self) -> Iterator[Any]:
        """Iterate over values."""
        return self.values()

    def __getitem__(self, key: Any) -> Any:
        """Get item by key."""
        result = self.find(key)
        if result is None:
            raise KeyError(str(key))
        return result

    def __setitem__(self, key: Any, value: Any) -> None:
        """Set item by key."""
        self.insert(key, value)

    def __contains__(self, key: Any) -> bool:
        """Check if key exists."""
        return self.find(key) is not None
    # Type checking properties
    @property

    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self._size == 0
    @property

    def is_list(self) -> bool:
        """Check if this is a list node."""
        return False
    @property

    def is_dict(self) -> bool:
        """Check if this is a dict node."""
        return True  # Trie is dict-like (maps strings to values)
    @property

    def is_reference(self) -> bool:
        """Check if this is a reference node."""
        return False
    @property

    def is_object(self) -> bool:
        """Check if this is an object node."""
        return False
    @property

    def type(self) -> str:
        """Get the type of this node."""
        return "trie"
    @property

    def value(self) -> Any:
        """Get the value of this node."""
        return self.to_native()
    @property

    def strategy_name(self) -> str:
        """Get strategy name."""
        return "TRIE"
    @property

    def supported_traits(self) -> NodeTrait:
        """Get supported traits."""
        return self.get_supported_traits()

    def add_edge(self, from_node: Any, to_node: Any, weight: float = 1.0) -> None:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph edges")

    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph edges")

    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph edges")

    def find_path(self, start: Any, end: Any) -> list[Any]:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph paths")

    def get_neighbors(self, node: Any) -> list[Any]:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph neighbors")

    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        """Not supported - this is a tree/map strategy, not a graph."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support graph edges")

    def as_union_find(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support union-find view")

    def as_neural_graph(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support neural graph view")

    def as_flow_network(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support flow network view")
