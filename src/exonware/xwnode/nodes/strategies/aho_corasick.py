#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/aho_corasick.py
Aho Corasick Node Strategy Implementation
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.22
Generation Date: 16-Jan-2026
"""

from __future__ import annotations
from collections.abc import AsyncIterator, Iterator
"""
Aho-Corasick Node Strategy Implementation
This module implements the AHO_CORASICK strategy for efficient multi-pattern
string matching using the Aho-Corasick automaton algorithm.
"""
from typing import Any
from collections import deque, defaultdict
from collections.abc import Callable
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait


class ACNode:
    """Node in the Aho-Corasick trie."""

    def __init__(self):
        """
        Initialize AC node.
        Time Complexity: O(1)
        """
        self.children: dict[str, ACNode] = {}
        self.failure: ACNode | None = None
        self.output: set[str] = set()  # Patterns that end at this node
        self.pattern_indices: set[int] = set()  # Indices of patterns
        self.depth = 0

    def is_leaf(self) -> bool:
        """
        Check if this is a leaf node.
        Time Complexity: O(1)
        """
        return len(self.children) == 0


class AhoCorasickStrategy(ANodeTreeStrategy):
    """
    Aho-Corasick node strategy for multi-pattern string matching.
    Efficiently searches for multiple patterns simultaneously in a text
    using a finite automaton with failure links for linear-time matching.
    # Strategy type classification
    STRATEGY_TYPE = NodeType.TREE
    """

    def __init__(self, traits: NodeTrait = NodeTrait.NONE, **options):
        """
        Initialize the Aho-Corasick strategy.
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        super().__init__(NodeMode.AHO_CORASICK, traits, **options)
        self.case_sensitive = options.get('case_sensitive', True)
        self.enable_overlapping = options.get('enable_overlapping', True)
        self.max_pattern_length = options.get('max_pattern_length', 1000)
        # Core automaton
        self._root = ACNode()
        self._patterns: list[str] = []
        self._pattern_to_index: dict[str, int] = {}
        self._automaton_built = False
        # Key-value mapping for compatibility
        self._values: dict[str, Any] = {}
        self._size = 0
        # Statistics
        self._total_nodes = 1  # Root node
        self._max_depth = 0
        self._search_cache: dict[str, list[tuple[str, int]]] = {}

    def get_supported_traits(self) -> NodeTrait:
        """
        Get the traits supported by the Aho-Corasick strategy.
        Time Complexity: O(1)
        """
        return (NodeTrait.ORDERED | NodeTrait.INDEXED | NodeTrait.STREAMING)

    def _preprocess_pattern(self, pattern: str) -> str:
        """
        Preprocess pattern based on settings.
        Time Complexity: O(|pattern|) - for case conversion if needed
        """
        if not self.case_sensitive:
            pattern = pattern.lower()
        return pattern

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text based on settings.
        Time Complexity: O(|text|) - for case conversion if needed
        """
        if not self.case_sensitive:
            text = text.lower()
        return text

    def _add_pattern_to_trie(self, pattern: str, pattern_index: int) -> None:
        """
        Add pattern to the trie structure.
        Time Complexity: O(|pattern|) - iterate through each character
        Space Complexity: O(|pattern|) - create at most |pattern| new nodes
        """
        current = self._root
        depth = 0
        for char in pattern:
            if char not in current.children:
                current.children[char] = ACNode()
                current.children[char].depth = depth + 1
                self._total_nodes += 1
            current = current.children[char]
            depth += 1
        # Mark end of pattern
        current.output.add(pattern)
        current.pattern_indices.add(pattern_index)
        self._max_depth = max(self._max_depth, depth)

    def _build_failure_links(self) -> None:
        """
        Build failure links using BFS.
        Time Complexity: O(N * Σ) where N is total nodes, Σ is alphabet size
        Space Complexity: O(N) for the queue
        """
        queue = deque()
        # Initialize failure links for root's children
        for child in self._root.children.values():
            child.failure = self._root
            queue.append(child)
        # Build failure links for all other nodes
        while queue:
            current = queue.popleft()
            for char, child in current.children.items():
                queue.append(child)
                # Find the failure link
                failure_node = current.failure
                while failure_node is not None and char not in failure_node.children:
                    failure_node = failure_node.failure
                if failure_node is not None:
                    child.failure = failure_node.children[char]
                else:
                    child.failure = self._root
                # Add output from failure node
                if child.failure:
                    child.output.update(child.failure.output)
                    child.pattern_indices.update(child.failure.pattern_indices)

    def _build_automaton(self) -> None:
        """
        Build the complete Aho-Corasick automaton.
        Time Complexity: O(N * Σ) where N is total nodes
        """
        if self._automaton_built:
            return
        # Build failure links
        self._build_failure_links()
        self._automaton_built = True
        self._search_cache.clear()

    def _rebuild_automaton(self) -> None:
        """
        Rebuild the automaton from scratch.
        Time Complexity: O(Σ|patterns| + N*Σ) - sum of pattern lengths + failure link construction
        Space Complexity: O(Σ|patterns|) - total nodes
        """
        # Reset automaton
        self._root = ACNode()
        self._total_nodes = 1
        self._max_depth = 0
        self._automaton_built = False
        self._search_cache.clear()
        # Rebuild trie
        for i, pattern in enumerate(self._patterns):
            self._add_pattern_to_trie(pattern, i)
        # Build failure links
        self._build_automaton()
    # ============================================================================
    # CORE OPERATIONS (Key-based interface for compatibility)
    # ============================================================================

    def put(self, key: Any, value: Any = None) -> None:
        """
        Add pattern to automaton.
        Time Complexity: O(|pattern|) - amortized, may trigger rebuild
        Space Complexity: O(|pattern|)
        """
        pattern = str(key)
        processed_pattern = self._preprocess_pattern(pattern)
        if len(processed_pattern) > self.max_pattern_length:
            raise ValueError(f"Pattern length {len(processed_pattern)} exceeds maximum {self.max_pattern_length}")
        if processed_pattern not in self._pattern_to_index:
            # Add new pattern
            pattern_index = len(self._patterns)
            self._patterns.append(processed_pattern)
            self._pattern_to_index[processed_pattern] = pattern_index
            # Add to trie
            self._add_pattern_to_trie(processed_pattern, pattern_index)
            self._automaton_built = False
            self._size += 1
        # Store value
        self._values[pattern] = value if value is not None else pattern

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get value by key.
        Time Complexity: O(1) - dictionary lookup
        """
        key_str = str(key)
        if key_str == "patterns":
            return self._patterns.copy()
        elif key_str == "automaton_info":
            return {
                'total_nodes': self._total_nodes,
                'max_depth': self._max_depth,
                'automaton_built': self._automaton_built,
                'pattern_count': len(self._patterns)
            }
        elif key_str in self._values:
            return self._values[key_str]
        return default

    def has(self, key: Any) -> bool:
        """
        Check if key exists.
        Time Complexity: O(|pattern|) - preprocessing + O(1) lookup
        """
        key_str = str(key)
        pattern = self._preprocess_pattern(key_str)
        return pattern in self._pattern_to_index or key_str in self._values

    def remove(self, key: Any) -> bool:
        """
        Remove pattern (requires automaton rebuild).
        Time Complexity: O(Σ|patterns|) - requires full rebuild
        Space Complexity: O(Σ|patterns|)
        """
        pattern = str(key)
        processed_pattern = self._preprocess_pattern(pattern)
        if processed_pattern in self._pattern_to_index:
            # Remove pattern
            index = self._pattern_to_index[processed_pattern]
            del self._pattern_to_index[processed_pattern]
            self._patterns.pop(index)
            # Update indices
            for i, p in enumerate(self._patterns):
                self._pattern_to_index[p] = i
            # Remove value
            self._values.pop(pattern, None)
            self._size -= 1
            # Rebuild automaton
            self._rebuild_automaton()
            return True
        return False

    def delete(self, key: Any) -> bool:
        """
        Remove pattern (alias for remove).
        Time Complexity: O(Σ|patterns|) - requires full rebuild
        """
        return self.remove(key)

    def clear(self) -> None:
        """
        Clear all patterns.
        Time Complexity: O(1) - just reset references
        Space Complexity: O(1)
        """
        self._root = ACNode()
        self._patterns.clear()
        self._pattern_to_index.clear()
        self._values.clear()
        self._search_cache.clear()
        self._total_nodes = 1
        self._max_depth = 0
        self._automaton_built = False
        self._size = 0

    def keys(self) -> Iterator[str]:
        """
        Get all pattern keys.
        Time Complexity: O(n) where n is number of patterns
        """
        for pattern in self._patterns:
            yield pattern
        yield "patterns"
        yield "automaton_info"

    def values(self) -> Iterator[Any]:
        """
        Get all values.
        Time Complexity: O(n) where n is number of patterns
        """
        for value in self._values.values():
            yield value
        yield self._patterns.copy()
        yield self.get("automaton_info")

    def items(self) -> Iterator[tuple[str, Any]]:
        """
        Get all key-value pairs.
        Time Complexity: O(n) where n is number of patterns
        """
        for key, value in self._values.items():
            yield (key, value)
        yield ("patterns", self._patterns.copy())
        yield ("automaton_info", self.get("automaton_info"))

    def __len__(self) -> int:
        """
        Get number of patterns.
        Time Complexity: O(1)
        """
        return self._size

    def to_native(self) -> dict[str, Any]:
        """
        Convert to native Python dict.
        Time Complexity: O(n) where n is number of patterns
        Space Complexity: O(n)
        """
        result = dict(self._values)
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
    @property

    def is_list(self) -> bool:
        """
        This can behave like a list for pattern access.
        Time Complexity: O(1)
        """
        return True
    @property

    def is_dict(self) -> bool:
        """
        This behaves like a dict.
        Time Complexity: O(1)
        """
        return True
    # ============================================================================
    # AHO-CORASICK SPECIFIC OPERATIONS
    # ============================================================================

    def add_pattern(self, pattern: str, metadata: Any = None) -> None:
        """
        Add pattern with optional metadata.
        Time Complexity: O(|pattern|)
        """
        self.put(pattern, metadata)

    def search_text(self, text: str) -> list[tuple[str, int, Any]]:
        """
        Search for all pattern matches in text.
        Time Complexity: O(|text| + |matches|) - linear in text length plus output
        Space Complexity: O(|matches|) - for storing results
        """
        if not text or not self._patterns:
            return []
        # Check cache
        cache_key = text[:100]  # Cache based on first 100 chars
        if cache_key in self._search_cache and len(text) <= 100:
            return self._search_cache[cache_key]
        processed_text = self._preprocess_text(text)
        self._build_automaton()
        matches = []
        current = self._root
        for i, char in enumerate(processed_text):
            # Follow failure links until we find a valid transition
            while current is not None and char not in current.children:
                current = current.failure
            if current is None:
                current = self._root
                continue
            current = current.children[char]
            # Report all patterns that end at this position
            for pattern in current.output:
                start_pos = i - len(pattern) + 1
                metadata = self._values.get(pattern, None)
                matches.append((pattern, start_pos, metadata))
        # Cache small results
        if len(text) <= 100:
            self._search_cache[cache_key] = matches
        return matches

    def find_all_matches(self, text: str) -> dict[str, list[int]]:
        """
        Find all positions where each pattern matches.
        Time Complexity: O(|text| + |matches|)
        Space Complexity: O(|matches|)
        """
        matches = self.search_text(text)
        result = defaultdict(list)
        for pattern, position, _ in matches:
            result[pattern].append(position)
        # Convert to regular dict
        return dict(result)

    def count_matches(self, text: str) -> dict[str, int]:
        """
        Count occurrences of each pattern.
        Time Complexity: O(|text| + |matches|)
        """
        matches = self.find_all_matches(text)
        return {pattern: len(positions) for pattern, positions in matches.items()}
    # ============================================================================
    # REQUIRED ABSTRACT METHODS (from ANodeTreeStrategy)
    # ============================================================================

    def traverse(self, order: str = 'inorder') -> list[Any]:
        """
        Traverse tree in specified order (inorder, preorder, postorder).
        For Aho-Corasick, returns all patterns in lexicographic order.
        """
        result = []
        self._collect_patterns(self._root, "", result, order)
        return result

    def _collect_patterns(self, node: ACNode, prefix: str, result: list[str], order: str) -> None:
        """Collect patterns from trie in specified order."""
        if order == 'preorder':
            if node.output:
                result.extend(sorted(node.output))
        for char in sorted(node.children.keys()):
            child = node.children[char]
            self._collect_patterns(child, prefix + char, result, order)
        if order == 'postorder':
            if node.output:
                result.extend(sorted(node.output))
        elif order == 'inorder':
            if node.output:
                result.extend(sorted(node.output))

    def get_min(self) -> Any:
        """Get minimum key (lexicographically smallest pattern)."""
        if not self._patterns:
            return None
        return min(self._patterns)

    def get_max(self) -> Any:
        """Get maximum key (lexicographically largest pattern)."""
        if not self._patterns:
            return None
        return max(self._patterns)
    # ============================================================================
    # BEHAVIORAL VIEWS (from ANodeTreeStrategy and ANodeGraphStrategy)
    # ============================================================================

    def as_trie(self):
        """Provide Trie behavioral view."""
        return self  # Aho-Corasick is already a trie-based structure

    def as_heap(self):
        """Provide Heap behavioral view."""
        raise NotImplementedError(
            "Aho-Corasick cannot behave as Heap - use HeapStrategy for priority-based operations"
        )

    def as_skip_list(self):
        """Provide SkipList behavioral view."""
        raise NotImplementedError(
            "Aho-Corasick cannot behave as SkipList - use SkipListStrategy for probabilistic sorted operations"
        )
    # Graph methods (from ANodeGraphStrategy)

    def add_edge(self, from_node: Any, to_node: Any, weight: float = 1.0) -> None:
        """Add edge between nodes (not applicable for Aho-Corasick)."""
        raise NotImplementedError(
            "Aho-Corasick does not support graph edges - use graph strategies for edge operations"
        )

    def remove_edge(self, from_node: Any, to_node: Any) -> bool:
        """Remove edge between nodes (not applicable for Aho-Corasick)."""
        raise NotImplementedError(
            "Aho-Corasick does not support graph edges"
        )

    def has_edge(self, from_node: Any, to_node: Any) -> bool:
        """Check if edge exists (not applicable for Aho-Corasick)."""
        raise NotImplementedError(
            "Aho-Corasick does not support graph edges"
        )

    def find_path(self, start: Any, end: Any) -> list[Any]:
        """Find path between nodes (not applicable for Aho-Corasick)."""
        raise NotImplementedError(
            "Aho-Corasick does not support graph paths"
        )

    def get_neighbors(self, node: Any) -> list[Any]:
        """Get neighboring nodes (not applicable for Aho-Corasick)."""
        raise NotImplementedError(
            "Aho-Corasick does not support graph neighbors"
        )

    def get_edge_weight(self, from_node: Any, to_node: Any) -> float:
        """Get edge weight (not applicable for Aho-Corasick)."""
        raise NotImplementedError(
            "Aho-Corasick does not support graph edges"
        )

    def as_union_find(self):
        """Provide Union-Find behavioral view."""
        raise NotImplementedError(
            "Aho-Corasick cannot behave as Union-Find - use UnionFindStrategy for connectivity operations"
        )

    def as_neural_graph(self):
        """Provide Neural Graph behavioral view."""
        raise NotImplementedError(
            "Aho-Corasick cannot behave as Neural Graph - use graph strategies for neural operations"
        )

    def as_flow_network(self):
        """Provide Flow Network behavioral view."""
        raise NotImplementedError(
            "Aho-Corasick cannot behave as Flow Network - use graph strategies for flow operations"
        )

    def has_any_match(self, text: str) -> bool:
        """
        Check if text contains any of the patterns.
        Time Complexity: O(|text|) - can terminate early on first match
        """
        if not text or not self._patterns:
            return False
        processed_text = self._preprocess_text(text)
        self._build_automaton()
        current = self._root
        for char in processed_text:
            while current is not None and char not in current.children:
                current = current.failure
            if current is None:
                current = self._root
                continue
            current = current.children[char]
            if current.output:
                return True
        return False

    def find_longest_match(self, text: str) -> tuple[str, int, int] | None:
        """
        Find the longest pattern match in text.
        Time Complexity: O(|text| + |matches|)
        """
        matches = self.search_text(text)
        if not matches:
            return None
        longest = max(matches, key=lambda x: len(x[0]))
        pattern, start_pos, _ = longest
        return pattern, start_pos, len(pattern)

    def replace_patterns(self, text: str, replacement_func: Callable[[str], str] | None = None) -> str:
        """
        Replace all pattern matches in text.
        Time Complexity: O(|text| + |matches| * |text|) - worst case due to string manipulation
        Space Complexity: O(|text|)
        """
        if not replacement_func:
            replacement_func = lambda pattern, metadata: f"[{pattern}]"
        matches = self.search_text(text)
        if not matches:
            return text
        # Sort matches by position (descending) to avoid index shifts
        matches.sort(key=lambda x: x[1], reverse=True)
        result = text
        for pattern, start_pos, metadata in matches:
            end_pos = start_pos + len(pattern)
            replacement = replacement_func(pattern, metadata)
            result = result[:start_pos] + replacement + result[end_pos:]
        return result

    def get_pattern_statistics(self) -> dict[str, Any]:
        """
        Get statistics about patterns and automaton.
        Time Complexity: O(Σ|patterns|) - sum of pattern lengths
        """
        if not self._patterns:
            return {'pattern_count': 0, 'total_nodes': 1, 'avg_pattern_length': 0}
        pattern_lengths = [len(p) for p in self._patterns]
        unique_chars = set()
        for pattern in self._patterns:
            unique_chars.update(pattern)
        return {
            'pattern_count': len(self._patterns),
            'total_nodes': self._total_nodes,
            'max_depth': self._max_depth,
            'avg_pattern_length': sum(pattern_lengths) / len(pattern_lengths),
            'min_pattern_length': min(pattern_lengths),
            'max_pattern_length': max(pattern_lengths),
            'unique_characters': len(unique_chars),
            'alphabet_size': len(unique_chars),
            'automaton_built': self._automaton_built,
            'cache_size': len(self._search_cache)
        }

    def validate_automaton(self) -> bool:
        """
        Validate the automaton structure.
        Time Complexity: O(N) where N is total nodes
        Space Complexity: O(N) for visited set
        """
        self._build_automaton()
        def _validate_node(node: ACNode, visited: set[ACNode]) -> bool:
            if node in visited:
                return True
            visited.add(node)
            # Check failure link
            if node != self._root and node.failure is None:
                return False
            # Check children
            for child in node.children.values():
                if not _validate_node(child, visited):
                    return False
            return True
        return _validate_node(self._root, set())

    def export_automaton(self) -> dict[str, Any]:
        """
        Export automaton structure for analysis.
        Time Complexity: O(N) where N is total nodes
        Space Complexity: O(N)
        """
        self._build_automaton()
        def _export_node(node: ACNode, node_id: int) -> dict[str, Any]:
            return {
                'id': node_id,
                'depth': node.depth,
                'children': list(node.children.keys()),
                'output': list(node.output),
                'has_failure': node.failure is not None
            }
        nodes = []
        node_queue = deque([(self._root, 0)])
        node_id = 0
        while node_queue:
            node, current_id = node_queue.popleft()
            nodes.append(_export_node(node, current_id))
            for child in node.children.values():
                node_id += 1
                node_queue.append((child, node_id))
        return {
            'nodes': nodes,
            'patterns': self._patterns.copy(),
            'statistics': self.get_pattern_statistics()
        }
    # ============================================================================
    # PERFORMANCE CHARACTERISTICS
    # ============================================================================
    @property

    def backend_info(self) -> dict[str, Any]:
        """
        Get backend implementation info.
        Time Complexity: O(1)
        """
        return {
            'strategy': 'AHO_CORASICK',
            'backend': 'Finite automaton with failure links',
            'case_sensitive': self.case_sensitive,
            'enable_overlapping': self.enable_overlapping,
            'max_pattern_length': self.max_pattern_length,
            'complexity': {
                'construction': 'O(Σ|patterns|)',  # Σ = alphabet size
                'search': 'O(|text| + |matches|)',
                'space': 'O(Σ|patterns|)',
                'pattern_addition': 'O(|pattern|)',
                'pattern_removal': 'O(Σ|patterns|)'  # Requires rebuild
            }
        }
    @property

    def metrics(self) -> dict[str, Any]:
        """
        Get performance metrics.
        Time Complexity: O(Σ|patterns|)
        """
        stats = self.get_pattern_statistics()
        return {
            'patterns': stats['pattern_count'],
            'nodes': stats['total_nodes'],
            'max_depth': stats['max_depth'],
            'avg_pattern_length': f"{stats['avg_pattern_length']:.1f}",
            'alphabet_size': stats['alphabet_size'],
            'automaton_built': stats['automaton_built'],
            'cache_entries': stats['cache_size'],
            'memory_usage': f"{stats['total_nodes'] * 100 + len(self._patterns) * 50} bytes (estimated)"
        }
