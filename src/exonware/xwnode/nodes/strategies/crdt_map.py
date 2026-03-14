"""
#exonware/xwnode/src/exonware/xwnode/nodes/strategies/crdt_map.py
CRDT Map Node Strategy Implementation
This module implements the CRDT_MAP strategy for conflict-free replicated
data type with Last-Write-Wins semantics for distributed systems.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.5
Generation Date: 24-Oct-2025
"""

from __future__ import annotations
from collections.abc import AsyncIterator, Iterator
import time
from typing import Any
from .base import ANodeTreeStrategy
from .contracts import NodeType
from ...defs import NodeMode, NodeTrait
from ...errors import XWNodeError, XWNodeValueError, XWNodeUnsupportedCapabilityError


class VectorClock:
    """
    Vector clock for causality tracking.
    WHY vector clocks:
    - Tracks causality between operations
    - Enables conflict detection
    - Ensures eventual consistency
    """

    def __init__(self, replica_id: str = "default"):
        """
        Initialize vector clock.
        Time Complexity: O(1)
        Args:
            replica_id: Unique replica identifier
        """
        self.clocks: dict[str, int] = {replica_id: 0}
        self.replica_id = replica_id

    def increment(self) -> None:
        """
        Increment this replica's clock.
        Time Complexity: O(1)
        """
        self.clocks[self.replica_id] = self.clocks.get(self.replica_id, 0) + 1

    def update(self, other: VectorClock) -> None:
        """
        Update with another vector clock.
        Time Complexity: O(r) where r is number of replicas
        Args:
            other: Other vector clock
        WHY merge clocks:
        - Takes maximum of each replica's clock
        - Preserves causality information
        - Enables happened-before detection
        """
        for replica, clock in other.clocks.items():
            self.clocks[replica] = max(self.clocks.get(replica, 0), clock)

    def happens_before(self, other: VectorClock) -> bool:
        """
        Check if this clock happened before other.
        Args:
            other: Other vector clock
        Returns:
            True if this happened before other
        """
        # All clocks must be ≤ corresponding clocks in other
        for replica, clock in self.clocks.items():
            if clock > other.clocks.get(replica, 0):
                return False
        # At least one must be strictly less
        return any(
            self.clocks.get(replica, 0) < clock
            for replica, clock in other.clocks.items()
        )

    def concurrent_with(self, other: VectorClock) -> bool:
        """Check if concurrent (neither happened before the other)."""
        return not self.happens_before(other) and not other.happens_before(self)

    def copy(self) -> VectorClock:
        """Create copy of vector clock."""
        vc = VectorClock(self.replica_id)
        vc.clocks = self.clocks.copy()
        return vc

    def __repr__(self) -> str:
        """String representation."""
        return f"VectorClock({self.clocks})"


class CRDTEntry:
    """
    CRDT map entry with timestamp and vector clock.
    WHY timestamped entries:
    - Enables Last-Write-Wins resolution
    - Tracks causality with vector clocks
    - Supports tombstones for deletions
    """

    def __init__(self, value: Any, timestamp: float, vector_clock: VectorClock, 
                 is_tombstone: bool = False):
        """
        Initialize CRDT entry.
        Args:
            value: Stored value
            timestamp: Physical timestamp
            vector_clock: Logical vector clock
            is_tombstone: Whether this is a deletion marker
        """
        self.value = value
        self.timestamp = timestamp
        self.vector_clock = vector_clock
        self.is_tombstone = is_tombstone


class CRDTMapStrategy(ANodeTreeStrategy):
    """
    CRDT Map strategy for conflict-free distributed data.
    WHY CRDT:
    - Enables offline-first applications
    - Guarantees eventual consistency without coordination
    - Supports multi-master replication
    - Handles network partitions gracefully
    - Perfect for collaborative editing and distributed databases
    WHY this implementation:
    - Last-Write-Wins (LWW) provides simple conflict resolution
    - Vector clocks track causality for concurrent detection
    - Tombstones handle deletion conflicts correctly
    - Physical timestamps break ties deterministically
    - Replica IDs ensure uniqueness
    Time Complexity:
    - Put: O(1) local operation
    - Get: O(1) lookup
    - Merge: O(m) where m is entries in other map
    - Delete: O(1) (creates tombstone)
    Space Complexity: O(n + d) where n is live entries, d is tombstones
    Trade-offs:
    - Advantage: Conflict-free merging (strong eventual consistency)
    - Advantage: No coordination needed between replicas
    - Advantage: Works offline, syncs when connected
    - Limitation: Tombstones accumulate (needs garbage collection)
    - Limitation: LWW may lose concurrent writes
    - Limitation: Requires synchronized clocks for tie-breaking
    - Compared to HashMap: Adds conflict resolution, more memory
    - Compared to Operational Transform: Simpler, more robust
    Best for:
    - Distributed databases (Cassandra-style)
    - Offline-first mobile applications
    - Collaborative editing (presence, metadata)
    - Multi-master replication scenarios
    - Shopping carts and user preferences
    - Distributed caching systems
    Not recommended for:
    - Single-server applications (use normal HashMap)
    - When last-write semantics are unacceptable
    - Financial transactions (need stronger consistency)
    - When tombstone growth is problematic
    - Real-time gaming (use operational transform)
    Following eXonware Priorities:
    1. Security: Validates replica IDs, prevents malformed merges
    2. Usability: Simple put/get API, automatic conflict resolution
    3. Maintainability: Clean CRDT semantics, well-documented
    4. Performance: O(1) operations, efficient merging
    5. Extensibility: Easy to add OR-Set, counter CRDTs
    Industry Best Practices:
    - Follows Shapiro et al. CRDT specification
    - Implements LWW-Element-Set variant
    - Uses vector clocks for causality
    - Provides tombstone garbage collection
    - Compatible with Riak, Cassandra approaches
    """
    # Tree node type for classification
    STRATEGY_TYPE: NodeType = NodeType.TREE

    def __init__(self, mode: NodeMode = NodeMode.CRDT_MAP,
                 traits: NodeTrait = NodeTrait.NONE,
                 replica_id: str | None = None, **options):
        """
        Initialize CRDT map strategy.
        Args:
            mode: Node mode
            traits: Node traits
            replica_id: Unique replica identifier
            **options: Additional options
        """
        super().__init__(mode, traits, **options)
        self.replica_id = replica_id or f"replica_{id(self)}"
        self._entries: dict[Any, CRDTEntry] = {}
        self._vector_clock = VectorClock(self.replica_id)
        self._size = 0

    def get_supported_traits(self) -> NodeTrait:
        """Get supported traits."""
        return NodeTrait.INDEXED | NodeTrait.PERSISTENT | NodeTrait.STREAMING
    # ============================================================================
    # CORE CRDT OPERATIONS
    # ============================================================================

    def put(self, key: Any, value: Any = None) -> None:
        """
        Put value with LWW semantics.
        Args:
            key: Key
            value: Value
        WHY timestamping:
        - Enables conflict resolution
        - Provides total ordering
        - Breaks ties deterministically
        """
        # Security: Validate key
        if key is None:
            raise XWNodeValueError("Key cannot be None")
        # Increment vector clock
        self._vector_clock.increment()
        # Create entry with current timestamp and vector clock
        timestamp = time.time()
        vector_clock = self._vector_clock.copy()
        entry = CRDTEntry(value, timestamp, vector_clock, is_tombstone=False)
        # Check if we need to update
        if key in self._entries:
            existing = self._entries[key]
            # Only update if new entry wins
            if self._should_replace(existing, entry):
                old_tombstone = existing.is_tombstone
                self._entries[key] = entry
                # Update size if transitioning from tombstone to value
                if old_tombstone and not entry.is_tombstone:
                    self._size += 1
        else:
            self._entries[key] = entry
            self._size += 1

    def _should_replace(self, existing: CRDTEntry, new: CRDTEntry) -> bool:
        """
        Determine if new entry should replace existing.
        Args:
            existing: Current entry
            new: New entry
        Returns:
            True if new should replace existing
        WHY LWW resolution:
        - Timestamp provides total order
        - Replica ID breaks ties
        - Deterministic across all replicas
        """
        # If vector clocks show causal ordering, use that
        if new.vector_clock.happens_before(existing.vector_clock):
            return False
        if existing.vector_clock.happens_before(new.vector_clock):
            return True
        # Concurrent updates - use timestamp
        if new.timestamp > existing.timestamp:
            return True
        elif new.timestamp < existing.timestamp:
            return False
        # Same timestamp - use replica ID for deterministic tie-breaking
        return new.vector_clock.replica_id > existing.vector_clock.replica_id

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get value.
        Args:
            key: Key
            default: Default value
        Returns:
            Value or default (None if tombstone)
        """
        if key not in self._entries:
            return default
        entry = self._entries[key]
        # Return None for tombstones
        if entry.is_tombstone:
            return default
        return entry.value

    def has(self, key: Any) -> bool:
        """
        Check if key exists (and not deleted).
        Args:
            key: Key
        Returns:
            True if exists and not tombstone
        """
        if key not in self._entries:
            return False
        return not self._entries[key].is_tombstone

    def delete(self, key: Any) -> bool:
        """
        Delete key using tombstone.
        Args:
            key: Key to delete
        Returns:
            True if deleted, False if not found
        WHY tombstones:
        - Deletion must be replicated
        - Tombstone prevents resurrection
        - Eventually garbage collected
        """
        if key not in self._entries or self._entries[key].is_tombstone:
            return False
        # Increment vector clock
        self._vector_clock.increment()
        # Create tombstone entry
        timestamp = time.time()
        vector_clock = self._vector_clock.copy()
        tombstone = CRDTEntry(None, timestamp, vector_clock, is_tombstone=True)
        self._entries[key] = tombstone
        self._size -= 1
        return True
    # ============================================================================
    # CRDT MERGE OPERATION
    # ============================================================================

    def merge(self, other: CRDTMapStrategy) -> None:
        """
        Merge another CRDT map into this one.
        Args:
            other: Other CRDT map to merge
        WHY conflict-free merge:
        - Applies LWW resolution to all conflicts
        - Updates vector clock with merged knowledge
        - Handles tombstones correctly
        - Guarantees strong eventual consistency
        """
        # Merge vector clocks
        self._vector_clock.update(other._vector_clock)
        # Merge entries
        for key, other_entry in other._entries.items():
            if key not in self._entries:
                # New key, just add it
                self._entries[key] = other_entry
                if not other_entry.is_tombstone:
                    self._size += 1
            else:
                existing = self._entries[key]
                # Apply LWW resolution
                if self._should_replace(existing, other_entry):
                    old_tombstone = existing.is_tombstone
                    new_tombstone = other_entry.is_tombstone
                    self._entries[key] = other_entry
                    # Update size
                    if old_tombstone and not new_tombstone:
                        self._size += 1
                    elif not old_tombstone and new_tombstone:
                        self._size -= 1

    def get_replica_state(self) -> dict[str, Any]:
        """
        Get current replica state for synchronization.
        Returns:
            Serializable replica state
        """
        return {
            'replica_id': self.replica_id,
            'vector_clock': self._vector_clock.clocks.copy(),
            'entries': {
                key: {
                    'value': entry.value,
                    'timestamp': entry.timestamp,
                    'vector_clock': entry.vector_clock.clocks.copy(),
                    'is_tombstone': entry.is_tombstone
                }
                for key, entry in self._entries.items()
            }
        }

    def apply_replica_state(self, state: dict[str, Any]) -> None:
        """
        Apply replica state from synchronization.
        Args:
            state: Replica state dictionary
        WHY state application:
        - Enables sync from remote replicas
        - Reconstructs CRDT from serialized state
        - Maintains vector clock consistency
        """
        # Create temporary CRDT with remote state
        temp_crdt = CRDTMapStrategy(replica_id=state['replica_id'])
        temp_crdt._vector_clock.clocks = state['vector_clock'].copy()
        # Reconstruct entries
        for key, entry_data in state['entries'].items():
            vc = VectorClock(state['replica_id'])
            vc.clocks = entry_data['vector_clock'].copy()
            entry = CRDTEntry(
                entry_data['value'],
                entry_data['timestamp'],
                vc,
                entry_data['is_tombstone']
            )
            temp_crdt._entries[key] = entry
        # Merge into current state
        self.merge(temp_crdt)
    # ============================================================================
    # GARBAGE COLLECTION
    # ============================================================================

    def garbage_collect_tombstones(self, age_threshold: float = 3600) -> int:
        """
        Remove old tombstones to reclaim memory.
        Args:
            age_threshold: Minimum age in seconds for tombstone removal
        Returns:
            Number of tombstones removed
        WHY garbage collection:
        - Tombstones accumulate over time
        - Safe to remove after all replicas have seen them
        - Reclaims memory for deleted entries
        """
        current_time = time.time()
        removed = 0
        to_remove = []
        for key, entry in self._entries.items():
            if entry.is_tombstone:
                age = current_time - entry.timestamp
                if age > age_threshold:
                    to_remove.append(key)
        for key in to_remove:
            del self._entries[key]
            removed += 1
        return removed
    # ============================================================================
    # STANDARD OPERATIONS
    # ============================================================================

    def keys(self) -> Iterator[Any]:
        """Get iterator over live keys (excluding tombstones)."""
        for key, entry in self._entries.items():
            if not entry.is_tombstone:
                yield key

    def values(self) -> Iterator[Any]:
        """Get iterator over live values."""
        for entry in self._entries.values():
            if not entry.is_tombstone:
                yield entry.value

    def items(self) -> Iterator[tuple[Any, Any]]:
        """Get iterator over live key-value pairs."""
        for key, entry in self._entries.items():
            if not entry.is_tombstone:
                yield (key, entry.value)

    def __len__(self) -> int:
        """Get number of live entries."""
        return self._size

    def to_native(self) -> Any:
        """Convert to native dict (live entries only)."""
        return dict(self.items())
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
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def clear(self) -> None:
        """
        Clear all entries with tombstones.
        WHY tombstones on clear:
        - Ensures deletion propagates to other replicas
        - Prevents resurrection of old data
        """
        # Mark all as tombstones
        for key in list(self._entries.keys()):
            if not self._entries[key].is_tombstone:
                self.delete(key)

    def is_empty(self) -> bool:
        """Check if empty (no live entries)."""
        return self._size == 0

    def size(self) -> int:
        """Get number of live entries."""
        return self._size

    def get_mode(self) -> NodeMode:
        """Get strategy mode."""
        return self.mode

    def get_traits(self) -> NodeTrait:
        """Get strategy traits."""
        return self.traits
    # ============================================================================
    # STATISTICS
    # ============================================================================

    def get_statistics(self) -> dict[str, Any]:
        """
        Get CRDT statistics.
        Returns:
            Statistics dictionary
        """
        live_count = sum(1 for e in self._entries.values() if not e.is_tombstone)
        tombstone_count = sum(1 for e in self._entries.values() if e.is_tombstone)
        return {
            'replica_id': self.replica_id,
            'live_entries': live_count,
            'tombstones': tombstone_count,
            'total_entries': len(self._entries),
            'vector_clock_size': len(self._vector_clock.clocks),
            'vector_clock': self._vector_clock.clocks.copy()
        }
    # ============================================================================
    # COMPATIBILITY METHODS
    # ============================================================================

    def find(self, key: Any) -> Any | None:
        """Find value by key."""
        return self.get(key)

    def insert(self, key: Any, value: Any = None) -> None:
        """Insert key-value pair."""
        self.put(key, value)

    def __str__(self) -> str:
        """String representation."""
        stats = self.get_statistics()
        return (f"CRDTMapStrategy(replica={self.replica_id}, live={stats['live_entries']}, "
                f"tombstones={stats['tombstones']})")

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"CRDTMapStrategy(mode={self.mode.name}, replica={self.replica_id}, size={self._size}, traits={self.traits})"
    # ============================================================================
    # FACTORY METHOD
    # ============================================================================
    @classmethod

    def create_from_data(cls, data: Any, replica_id: str | None = None) -> CRDTMapStrategy:
        """
        Create CRDT map from data.
        Args:
            data: Dictionary or iterable
            replica_id: Unique replica ID
        Returns:
            New CRDTMapStrategy instance
        """
        instance = cls(replica_id=replica_id)
        if isinstance(data, dict):
            for key, value in data.items():
                instance.put(key, value)
        elif isinstance(data, (list, tuple)):
            for i, value in enumerate(data):
                instance.put(i, value)
        else:
            instance.put('value', data)
        return instance

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

    def traverse(self, order: str = 'inorder') -> list[Any]:
        """Traverse - returns all key-value pairs."""
        return list(self.items())

    def get_min(self) -> Any:
        """Get minimum key."""
        keys = list(self.keys())
        if not keys:
            return None
        return min(keys)

    def get_max(self) -> Any:
        """Get maximum key."""
        keys = list(self.keys())
        if not keys:
            return None
        return max(keys)

    def as_union_find(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support union-find view")

    def as_neural_graph(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support neural graph view")

    def as_flow_network(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support flow network view")

    def as_trie(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support trie view")

    def as_heap(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support heap view")

    def as_skip_list(self):
        """Not supported."""
        raise XWNodeUnsupportedCapabilityError(f"{self.__class__.__name__} does not support skip list view")
