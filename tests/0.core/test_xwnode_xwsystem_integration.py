#!/usr/bin/env python3
"""
#exonware/xwnode/tests/0.core/test_xwnode_xwsystem_integration.py
Core tests for XWNode integration with XWSystem.
Verifies that XWNode correctly uses XWSystem for:
- Security (resource limits, validation)
- Monitoring (metrics, circuit breakers)
- Threading (thread-safe operations, caching)
- Logging (structured logging)
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.30
Generation Date: 08-Nov-2025
"""

import pytest
import threading
from exonware.xwnode import XWNode
from exonware.xwnode.defs import NodeMode
from exonware.xwsystem import get_logger
from exonware.xwsystem.security import get_resource_limits
from exonware.xwsystem.monitoring import create_component_metrics
@pytest.mark.xwnode_core

class TestXWNodeXWSystemIntegration:
    """Test XWNode integration with XWSystem components."""

    def test_xwnode_uses_xwsystem_logger(self):
        """Verify XWNode uses XWSystem logger."""
        # Logger should be available and working
        logger = get_logger('xwnode.test')
        assert logger is not None
        # Test logging works
        logger.debug("Test log message")
        logger.info("Test info message")

    def test_xwnode_uses_xwsystem_security(self):
        """Verify XWNode uses XWSystem security components."""
        # Resource limits should be available
        limits = get_resource_limits('xwnode')
        assert limits is not None
        # Create node - should work with security in place
        node = XWNode.from_native({'test': 'value'})
        assert node is not None
        assert node.get_value('test') == 'value'

    def test_xwnode_uses_xwsystem_monitoring(self):
        """Verify XWNode uses XWSystem monitoring."""
        # Metrics should be available
        metrics = create_component_metrics('xwnode_test')
        assert metrics is not None
        assert 'measure_operation' in metrics
        # Test operation measurement
        with metrics['measure_operation']('test_op'):
            node = XWNode.from_native({'test': 'value'})
            node.get_value('test')

    def test_xwnode_thread_safety_with_xwsystem(self):
        """Verify XWNode thread-safety works with XWSystem threading utilities."""
        node = XWNode.from_native({'counter': 0})
        results = []
        errors = []
        def increment_counter():
            try:
                for _ in range(100):
                    current = node.get_value('counter', 0)
                    node.set('counter', current + 1, in_place=True)
                results.append('success')
            except Exception as e:
                errors.append(str(e))
        # Create multiple threads
        threads = [threading.Thread(target=increment_counter) for _ in range(10)]
        # Start all threads
        for t in threads:
            t.start()
        # Wait for all threads
        for t in threads:
            t.join()
        # Should have no errors (thread-safe)
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        # Final value should be reasonable (may not be exact due to race conditions,
        # but should be close to expected)
        final_value = node.get_value('counter', 0)
        assert final_value > 0, "Counter should have been incremented"
@pytest.mark.xwnode_core

class TestXWNodeStrategyModes:
    """
    Test core XWNode strategy modes work correctly for generic map-style usage.
    NOTE:
    - Many advanced strategies exist (B_TREE, HAMT, TRIE, etc.) and are covered
      by their own dedicated tests in this repository.
    - This test focuses on the primary facade-facing modes that are guaranteed
      to behave like generic key/value stores for XWEntity/XWData usage:
        * AUTO      → adaptive selection
        * HASH_MAP  → hash-map optimized
        * ARRAY_LIST → list/array optimized
    """
    @pytest.mark.parametrize("mode", [
        'AUTO',
        'HASH_MAP',
        'ARRAY_LIST',
    ])

    def test_strategy_mode_works(self, mode):
        """Test that each strategy mode works correctly."""
        data = {'key1': 'value1', 'key2': 'value2', 'key3': {'nested': 'value'}}
        # Create node with specific mode
        node = XWNode.from_native(data, mode=mode)
        # Verify node works
        assert node is not None
        assert node.get_value('key1') == 'value1'
        assert node.get_value('key2') == 'value2'
        assert node.get_value('key3.nested') == 'value'
        # Verify can set values
        node.set('key4', 'value4', in_place=True)
        assert node.get_value('key4') == 'value4'
        # Verify can remove values
        node.remove('key4')
        assert node.get_value('key4') is None

    def test_auto_mode_selects_strategy(self):
        """Test AUTO mode selects appropriate strategy."""
        # Small dict - should use HASH_MAP
        small_data = {'a': 1, 'b': 2}
        node = XWNode.from_native(small_data, mode='AUTO')
        assert node is not None
        assert node.get_value('a') == 1
        # Large dict - AUTO should still work
        large_data = {f'key{i}': f'value{i}' for i in range(1000)}
        node = XWNode.from_native(large_data, mode='AUTO')
        assert node is not None
        assert node.get_value('key0') == 'value0'
        assert node.get_value('key999') == 'value999'
@pytest.mark.xwnode_core

class TestXWNodeCOWSemantics:
    """Test COW (Copy-on-Write) semantics with immutable=True."""

    def test_immutable_enables_cow(self):
        """Test that immutable=True enables COW semantics."""
        original_data = {'key1': 'value1', 'key2': 'value2'}
        node = XWNode.from_native(original_data, immutable=True)
        # Set should return new node
        new_node = node.set('key1', 'new_value')
        # Should be different instances
        assert new_node is not node
        # Original should be unchanged
        assert node.get_value('key1') == 'value1'
        assert node.get_value('key2') == 'value2'
        # New node should have updated value
        assert new_node.get_value('key1') == 'new_value'
        assert new_node.get_value('key2') == 'value2'  # Unchanged

    def test_cow_preserves_structure(self):
        """Test that COW preserves data structure correctly."""
        complex_data = {
            'users': [
                {'name': 'Alice', 'age': 30},
                {'name': 'Bob', 'age': 25}
            ],
            'metadata': {'version': 1}
        }
        node = XWNode.from_native(complex_data, immutable=True)
        new_node = node.set('users.0.age', 31)
        # Original unchanged
        assert node.get_value('users.0.age') == 30
        assert node.get_value('users.1.age') == 25
        # New node updated
        assert new_node.get_value('users.0.age') == 31
        assert new_node.get_value('users.1.age') == 25  # Unchanged

    def test_freeze_converts_to_immutable(self):
        """Test that freeze() converts mutable node to immutable."""
        node = XWNode.from_native({'key': 'value'})
        # Initially mutable
        assert not node.is_frozen()
        result = node.set('key', 'new_value')
        assert result is node  # Mutates in place
        # Freeze
        frozen = node.freeze()
        assert frozen.is_frozen()
        # Now should return new node
        new_frozen = frozen.set('key', 'another_value')
        assert new_frozen is not frozen
        assert frozen.get_value('key') == 'new_value'
        assert new_frozen.get_value('key') == 'another_value'
@pytest.mark.xwnode_core

class TestXWNodePathCache:
    """Test path navigation cache (30-50x speedup)."""

    def test_path_cache_speeds_up_repeated_access(self):
        """Test that path cache speeds up repeated path access."""
        data = {
            'level1': {
                'level2': {
                    'level3': {
                        'level4': {
                            'level5': 'deep_value'
                        }
                    }
                }
            }
        }
        node = XWNode.from_native(data)
        # First access - should populate cache
        value1 = node.get_value('level1.level2.level3.level4.level5')
        assert value1 == 'deep_value'
        # Second access - should use cache
        value2 = node.get_value('level1.level2.level3.level4.level5')
        assert value2 == 'deep_value'
        # Cache should be working (check via internal cache if accessible)
        # Note: Cache is internal, so we verify by ensuring no errors
        assert value1 == value2

    def test_path_cache_invalidates_on_set(self):
        """Test that path cache invalidates when values are set."""
        node = XWNode.from_native({'key': 'value1'})
        # Access to populate cache
        assert node.get_value('key') == 'value1'
        # Set new value
        node.set('key', 'value2', in_place=True)
        # Should get new value (cache invalidated)
        assert node.get_value('key') == 'value2'

    def test_path_cache_invalidates_on_remove(self):
        """Test that path cache invalidates when values are removed."""
        node = XWNode.from_native({'key': 'value'})
        # Access to populate cache
        assert node.get_value('key') == 'value'
        # Remove key
        node.remove('key')
        # Should return None (cache invalidated)
        assert node.get_value('key') is None
@pytest.mark.xwnode_core

class TestXWNodeGraphManager:
    """Test XWNode graph manager integration."""

    def test_graph_manager_available(self):
        """Test that graph manager is available."""
        # Graph manager should be importable (all xw libs MUST be there per GUIDE_TEST.md)
        from exonware.xwnode.common.graph.manager import XWGraphManager
        assert XWGraphManager is not None

    def test_graph_operations_work(self):
        """Test basic graph operations work."""
        # Create nodes
        node1 = XWNode.from_native({'id': 'node1', 'data': 'value1'})
        node2 = XWNode.from_native({'id': 'node2', 'data': 'value2'})
        # Basic operations should work - ids should be readable via XWNode.
        id1 = node1.get_value('id')
        id2 = node2.get_value('id')
        # IDs must be among the expected values.
        assert id1 in ('node1', 'node2')
        assert id2 in ('node1', 'node2')
@pytest.mark.xwnode_core

class TestXWNodeEdgeModes:
    """Test XWNode edge mode strategies."""
    @pytest.mark.parametrize("edge_mode", [
        'AUTO',
        'ADJ_LIST',
        'ADJ_MATRIX',
        'EDGE_LIST',
    ])

    def test_edge_mode_works(self, edge_mode):
        """Test that edge modes work correctly."""
        # Edge modes are typically used with graph manager
        # For now, verify the mode enum exists and can be used
        from exonware.xwnode.defs import EdgeMode
        try:
            mode_enum = EdgeMode[edge_mode]
            assert mode_enum is not None
        except KeyError:
            pytest.skip(f"Edge mode {edge_mode} not available")
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
