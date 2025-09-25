"""
Strategy Registry

This module provides the StrategyRegistry class for managing strategy registration,
discovery, and instantiation in the strategy system.
"""

import threading
from typing import Dict, Type, List, Optional, Any, Callable
from src.xlib.xwsystem.logging_setup import get_logger
from .types import NodeMode, EdgeMode, NodeTrait, EdgeTrait, NODE_STRATEGY_METADATA, EDGE_STRATEGY_METADATA
from ..errors import xNodeStrategyNotFoundError, xNodeStrategyInitializationError

logger = get_logger(__name__)


class StrategyRegistry:
    """
    Central registry for managing strategy implementations.
    
    This class provides thread-safe registration and discovery of strategy
    implementations for both nodes and edges in the strategy system.
    """
    
    def __init__(self):
        """Initialize the strategy registry."""
        self._node_strategies: Dict[NodeMode, Type] = {}
        self._edge_strategies: Dict[EdgeMode, Type] = {}
        self._node_factories: Dict[NodeMode, Callable] = {}
        self._edge_factories: Dict[EdgeMode, Callable] = {}
        self._lock = threading.RLock()
        
        # Register default strategies
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register default strategy implementations."""
        try:
            # Import default strategies
            from .impls.edge_adj_list import xAdjListStrategy
            from .impls.edge_adj_matrix import xAdjMatrixStrategy
            from .impls.edge_csr import xCSRStrategy
            from .impls.edge_dynamic_adj_list import xDynamicAdjListStrategy
            from .impls.edge_temporal_edgeset import xTemporalEdgeSetStrategy
            from .impls.edge_hyperedge_set import xHyperEdgeSetStrategy
            from .impls.edge_rtree import xRTreeStrategy
            from .impls.edge_flow_network import xFlowNetworkStrategy
            from .impls.edge_neural_graph import xNeuralGraphStrategy
            from .impls.edge_csc import xCSCStrategy
            from .impls.edge_bidir_wrapper import xBidirWrapperStrategy
            from .impls.edge_quadtree import xQuadtreeStrategy
            from .impls.edge_coo import xCOOStrategy
            from .impls.edge_octree import xOctreeStrategy
            from .impls.edge_property_store import xEdgePropertyStoreStrategy
            
            # Import new strategy implementations
            from .impls.node_hash_map import xHashMapStrategy
            from .impls.node_array_list import xArrayListStrategy
            from .impls.node_trie import xTrieStrategy
            from .impls.node_heap import xHeapStrategy
            from .impls.node_btree import xBTreeStrategy
            from .impls.node_union_find import xUnionFindStrategy
            from .impls.node_segment_tree import xSegmentTreeStrategy
            from .impls.node_lsm_tree import xLSMTreeStrategy
            from .impls.node_fenwick_tree import xFenwickTreeStrategy
            from .impls.node_set_hash import xSetHashStrategy
            from .impls.node_bloom_filter import xBloomFilterStrategy
            from .impls.node_cuckoo_hash import xCuckooHashStrategy
            from .impls.node_bitmap import xBitmapStrategy
            from .impls.node_roaring_bitmap import xRoaringBitmapStrategy
            from .impls.node_suffix_array import xSuffixArrayStrategy
            from .impls.node_aho_corasick import xAhoCorasickStrategy
            from .impls.node_count_min_sketch import xCountMinSketchStrategy
            from .impls.node_hyperloglog import xHyperLogLogStrategy
            from .impls.node_set_tree import xSetTreeStrategy
            from .impls.node_linked_list import xLinkedListStrategy
            from .impls.node_ordered_map import xOrderedMapStrategy
            from .impls.node_radix_trie import xRadixTrieStrategy
            from .impls.node_patricia import xPatriciaStrategy
            from .impls.node_b_plus_tree import xBPlusTreeStrategy
            from .impls.node_persistent_tree import xPersistentTreeStrategy
            from .impls.node_cow_tree import xCOWTreeStrategy
            from .impls.node_ordered_map_balanced import xOrderedMapBalancedStrategy
            from .impls.node_bitset_dynamic import xBitsetDynamicStrategy
            from .impls.edge_block_adj_matrix import xBlockAdjMatrixStrategy
            
            # Import data interchange optimized strategy
            try:
                from .impls.node_xdata_optimized import DataInterchangeOptimizedStrategy
            except ImportError:
                logger.warning("⚠️ DataInterchangeOptimizedStrategy not available")
                DataInterchangeOptimizedStrategy = None
            
            # Register tree-graph hybrid strategies
            try:
                from .impls.node_tree_graph_hybrid import TreeGraphHybridStrategy
                self.register_node_strategy(NodeMode.TREE_GRAPH_HYBRID, TreeGraphHybridStrategy)
            except ImportError:
                logger.warning("⚠️ TreeGraphHybridStrategy not available")
            
            # Register edge strategies
            self.register_edge_strategy(EdgeMode.ADJ_LIST, xAdjListStrategy)
            self.register_edge_strategy(EdgeMode.ADJ_MATRIX, xAdjMatrixStrategy)
            self.register_edge_strategy(EdgeMode.CSR, xCSRStrategy)
            self.register_edge_strategy(EdgeMode.DYNAMIC_ADJ_LIST, xDynamicAdjListStrategy)
            self.register_edge_strategy(EdgeMode.TEMPORAL_EDGESET, xTemporalEdgeSetStrategy)
            self.register_edge_strategy(EdgeMode.HYPEREDGE_SET, xHyperEdgeSetStrategy)
            self.register_edge_strategy(EdgeMode.R_TREE, xRTreeStrategy)
            self.register_edge_strategy(EdgeMode.FLOW_NETWORK, xFlowNetworkStrategy)
            self.register_edge_strategy(EdgeMode.NEURAL_GRAPH, xNeuralGraphStrategy)
            self.register_edge_strategy(EdgeMode.CSC, xCSCStrategy)
            self.register_edge_strategy(EdgeMode.BIDIR_WRAPPER, xBidirWrapperStrategy)
            self.register_edge_strategy(EdgeMode.QUADTREE, xQuadtreeStrategy)
            self.register_edge_strategy(EdgeMode.COO, xCOOStrategy)
            self.register_edge_strategy(EdgeMode.OCTREE, xOctreeStrategy)
            self.register_edge_strategy(EdgeMode.EDGE_PROPERTY_STORE, xEdgePropertyStoreStrategy)
            
            # Register new node strategies
            self.register_node_strategy(NodeMode.HASH_MAP, xHashMapStrategy)
            self.register_node_strategy(NodeMode.ARRAY_LIST, xArrayListStrategy)
            self.register_node_strategy(NodeMode.TRIE, xTrieStrategy)
            self.register_node_strategy(NodeMode.HEAP, xHeapStrategy)
            self.register_node_strategy(NodeMode.B_TREE, xBTreeStrategy)
            self.register_node_strategy(NodeMode.UNION_FIND, xUnionFindStrategy)
            self.register_node_strategy(NodeMode.SEGMENT_TREE, xSegmentTreeStrategy)
            self.register_node_strategy(NodeMode.LSM_TREE, xLSMTreeStrategy)
            self.register_node_strategy(NodeMode.FENWICK_TREE, xFenwickTreeStrategy)
            self.register_node_strategy(NodeMode.SET_HASH, xSetHashStrategy)
            self.register_node_strategy(NodeMode.BLOOM_FILTER, xBloomFilterStrategy)
            self.register_node_strategy(NodeMode.CUCKOO_HASH, xCuckooHashStrategy)
            self.register_node_strategy(NodeMode.BITMAP, xBitmapStrategy)
            self.register_node_strategy(NodeMode.ROARING_BITMAP, xRoaringBitmapStrategy)
            self.register_node_strategy(NodeMode.SUFFIX_ARRAY, xSuffixArrayStrategy)
            self.register_node_strategy(NodeMode.AHO_CORASICK, xAhoCorasickStrategy)
            self.register_node_strategy(NodeMode.COUNT_MIN_SKETCH, xCountMinSketchStrategy)
            self.register_node_strategy(NodeMode.HYPERLOGLOG, xHyperLogLogStrategy)
            self.register_node_strategy(NodeMode.SET_TREE, xSetTreeStrategy)
            self.register_node_strategy(NodeMode.LINKED_LIST, xLinkedListStrategy)
            self.register_node_strategy(NodeMode.ORDERED_MAP, xOrderedMapStrategy)
            self.register_node_strategy(NodeMode.RADIX_TRIE, xRadixTrieStrategy)
            self.register_node_strategy(NodeMode.PATRICIA, xPatriciaStrategy)
            self.register_node_strategy(NodeMode.B_PLUS_TREE, xBPlusTreeStrategy)
            self.register_node_strategy(NodeMode.PERSISTENT_TREE, xPersistentTreeStrategy)
            self.register_node_strategy(NodeMode.COW_TREE, xCOWTreeStrategy)
            self.register_node_strategy(NodeMode.ORDERED_MAP_BALANCED, xOrderedMapBalancedStrategy)
            self.register_node_strategy(NodeMode.BITSET_DYNAMIC, xBitsetDynamicStrategy)
            
            # Edge strategies
            self.register_edge_strategy(EdgeMode.BLOCK_ADJ_MATRIX, xBlockAdjMatrixStrategy)
            
            # Register data interchange optimized strategy factory
            # Note: This will be used by strategy manager when DATA_INTERCHANGE_OPTIMIZED preset is detected
            self.register_data_interchange_optimized_factory()
            
            logger.info("✅ Registered default strategies")
            
        except ImportError as e:
            logger.warning(f"⚠️ Could not register default strategies: {e}")
    
    def register_data_interchange_optimized_factory(self):
        """Register special factory for DATA_INTERCHANGE_OPTIMIZED preset handling."""
        # We'll store this in a special attribute for the strategy manager to use
        def data_interchange_factory(**options):
            from .impls.node_xdata_optimized import DataInterchangeOptimizedStrategy
            return DataInterchangeOptimizedStrategy(NodeTrait.INDEXED, **options)
        
        self._data_interchange_optimized_factory = data_interchange_factory
        logger.debug("📝 Registered data interchange optimized strategy factory")
    
    def get_data_interchange_optimized_factory(self):
        """Get the data interchange optimized strategy factory."""
        return getattr(self, '_data_interchange_optimized_factory', None)
    
    def register_node_strategy(self, mode: NodeMode, strategy_class: Type, 
                             factory: Optional[Callable] = None) -> None:
        """
        Register a node strategy implementation.
        
        Args:
            mode: The node mode to register
            strategy_class: The strategy implementation class
            factory: Optional factory function for custom instantiation
        """
        with self._lock:
            self._node_strategies[mode] = strategy_class
            if factory:
                self._node_factories[mode] = factory
            
            logger.debug(f"📝 Registered node strategy: {mode.name} -> {strategy_class.__name__}")
    
    def register_edge_strategy(self, mode: EdgeMode, strategy_class: Type,
                             factory: Optional[Callable] = None) -> None:
        """
        Register an edge strategy implementation.
        
        Args:
            mode: The edge mode to register
            strategy_class: The strategy implementation class
            factory: Optional factory function for custom instantiation
        """
        with self._lock:
            self._edge_strategies[mode] = strategy_class
            if factory:
                self._edge_factories[mode] = factory
            
            logger.debug(f"📝 Registered edge strategy: {mode.name} -> {strategy_class.__name__}")
    
    def get_node_strategy(self, mode: NodeMode, **kwargs) -> Any:
        """
        Get a node strategy instance.
        
        Args:
            mode: The node mode to instantiate
            **kwargs: Arguments to pass to the strategy constructor
            
        Returns:
            Strategy instance
            
        Raises:
            StrategyNotFoundError: If the strategy is not registered
            StrategyInitializationError: If strategy initialization fails
        """
        with self._lock:
            if mode not in self._node_strategies:
                raise xNodeStrategyNotFoundError(message=f"Strategy '{mode.name}' not found for node")
            
            strategy_class = self._node_strategies[mode]
            
            try:
                if mode in self._node_factories:
                    return self._node_factories[mode](**kwargs)
                else:
                    # Handle new interface that doesn't accept traits and other arguments
                    if mode == NodeMode.TREE_GRAPH_HYBRID:
                        # For TreeGraphHybridStrategy, ignore traits and other arguments
                        return strategy_class()
                    else:
                        return strategy_class(**kwargs)
                    
            except Exception as e:
                raise xNodeStrategyInitializationError(message=f"Failed to initialize strategy '{mode.name}': {e}", cause=e)
    
    def get_edge_strategy(self, mode: EdgeMode, **kwargs) -> Any:
        """
        Get an edge strategy instance.
        
        Args:
            mode: The edge mode to instantiate
            **kwargs: Arguments to pass to the strategy constructor
            
        Returns:
            Strategy instance
            
        Raises:
            StrategyNotFoundError: If the strategy is not registered
            StrategyInitializationError: If strategy initialization fails
        """
        with self._lock:
            if mode not in self._edge_strategies:
                raise xNodeStrategyNotFoundError(message=f"Strategy '{mode.name}' not found for edge")
            
            strategy_class = self._edge_strategies[mode]
            
            try:
                if mode in self._edge_factories:
                    return self._edge_factories[mode](**kwargs)
                else:
                    return strategy_class(**kwargs)
                    
            except Exception as e:
                raise xNodeStrategyInitializationError(message=f"Failed to initialize strategy '{mode.name}': {e}", cause=e)
    
    def list_node_modes(self) -> List[NodeMode]:
        """List all registered node modes."""
        with self._lock:
            return list(self._node_strategies.keys())
    
    def list_edge_modes(self) -> List[EdgeMode]:
        """List all registered edge modes."""
        with self._lock:
            return list(self._edge_strategies.keys())
    
    def get_node_metadata(self, mode: NodeMode) -> Optional[Any]:
        """Get metadata for a node mode."""
        return NODE_STRATEGY_METADATA.get(mode)
    
    def get_edge_metadata(self, mode: EdgeMode) -> Optional[Any]:
        """Get metadata for an edge mode."""
        return EDGE_STRATEGY_METADATA.get(mode)
    
    def has_node_strategy(self, mode: NodeMode) -> bool:
        """Check if a node strategy is registered."""
        with self._lock:
            return mode in self._node_strategies
    
    def has_edge_strategy(self, mode: EdgeMode) -> bool:
        """Check if an edge strategy is registered."""
        with self._lock:
            return mode in self._edge_strategies
    
    def unregister_node_strategy(self, mode: NodeMode) -> bool:
        """
        Unregister a node strategy.
        
        Returns:
            True if strategy was unregistered, False if not found
        """
        with self._lock:
            if mode in self._node_strategies:
                del self._node_strategies[mode]
                if mode in self._node_factories:
                    del self._node_factories[mode]
                logger.debug(f"🗑️ Unregistered node strategy: {mode.name}")
                return True
            return False
    
    def unregister_edge_strategy(self, mode: EdgeMode) -> bool:
        """
        Unregister an edge strategy.
        
        Returns:
            True if strategy was unregistered, False if not found
        """
        with self._lock:
            if mode in self._edge_strategies:
                del self._edge_strategies[mode]
                if mode in self._edge_factories:
                    del self._edge_factories[mode]
                logger.debug(f"🗑️ Unregistered edge strategy: {mode.name}")
                return True
            return False
    
    def clear_node_strategies(self) -> None:
        """Clear all registered node strategies."""
        with self._lock:
            self._node_strategies.clear()
            self._node_factories.clear()
            logger.info("🗑️ Cleared all node strategies")
    
    def clear_edge_strategies(self) -> None:
        """Clear all registered edge strategies."""
        with self._lock:
            self._edge_strategies.clear()
            self._edge_factories.clear()
            logger.info("🗑️ Cleared all edge strategies")
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            return {
                "node_strategies": len(self._node_strategies),
                "edge_strategies": len(self._edge_strategies),
                "node_factories": len(self._node_factories),
                "edge_factories": len(self._edge_factories),
                "registered_node_modes": [mode.name for mode in self._node_strategies.keys()],
                "registered_edge_modes": [mode.name for mode in self._edge_strategies.keys()]
            }


# Global registry instance
_registry = None


def get_registry() -> StrategyRegistry:
    """Get the global strategy registry instance."""
    global _registry
    if _registry is None:
        _registry = StrategyRegistry()
    return _registry


def register_node_strategy(mode: NodeMode, strategy_class: Type, 
                         factory: Optional[Callable] = None) -> None:
    """Register a node strategy with the global registry."""
    get_registry().register_node_strategy(mode, strategy_class, factory)


def register_edge_strategy(mode: EdgeMode, strategy_class: Type,
                         factory: Optional[Callable] = None) -> None:
    """Register an edge strategy with the global registry."""
    get_registry().register_edge_strategy(mode, strategy_class, factory)
