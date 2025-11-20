#!/usr/bin/env python3
"""
#exonware/xwnode/tests/0.core/test_core_cow.py

Core tests for Copy-on-Write (COW) functionality in XWNode.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.27
Generation Date: 26-Oct-2025
"""

import pytest
from exonware.xwnode import XWNode


@pytest.mark.xwnode_core
class TestCOWCore:
    """Core COW functionality tests - immutability and performance."""
    
    def test_mutable_by_default_backward_compat(self):
        """Test that nodes are mutable by default (backward compatibility)."""
        node = XWNode.from_native({'key': 'value1'})
        
        # Should mutate in place
        result = node.set('key', 'value2')
        
        # Returns self
        assert result is node
        # Check via to_native (COW uses different internal representation)
        assert node.to_native()['key'] == 'value2'
    
    def test_immutable_flag_enables_cow(self):
        """Test that immutable=True enables COW semantics."""
        node = XWNode.from_native({'key': 'value1'}, immutable=True)
        
        # Should return new node
        node2 = node.set('key', 'value2')
        
        # Different instances
        assert node2 is not node
        
        # Original unchanged via to_native
        assert node.to_native()['key'] == 'value1'
        
        # New node has new value
        assert node2.to_native()['key'] == 'value2'
    
    def test_freeze_converts_to_immutable(self):
        """Test freeze() converts mutable to immutable."""
        node = XWNode.from_native({'key': 'value1'})
        
        # Initially mutable
        assert not node.is_frozen()
        
        # Freeze it
        frozen = node.freeze()
        
        # Now immutable
        assert frozen.is_frozen()
        assert frozen is node  # freeze() returns self
        
        # Mutations now return new nodes
        node2 = frozen.set('key', 'value2')
        assert node2 is not frozen
        assert frozen.to_native()['key'] == 'value1'  # Original unchanged
        assert node2.to_native()['key'] == 'value2'  # New node has new value
    
    def test_cow_with_nested_paths(self):
        """Test COW with nested path mutations."""
        data = {
            'user': {
                'name': 'Alice',
                'age': 30
            }
        }
        node = XWNode.from_native(data, immutable=True)
        
        # Modify nested path
        node2 = node.set('user.name', 'Bob')
        
        # Original unchanged
        orig_native = node.to_native()
        assert orig_native['user']['name'] == 'Alice'
        assert orig_native['user']['age'] == 30
        
        # New node has changes
        new_native = node2.to_native()
        assert new_native['user']['name'] == 'Bob'
        assert new_native['user']['age'] == 30  # Other values preserved
    
    def test_multiple_mutations_preserve_history(self):
        """Test that multiple mutations create independent versions."""
        original = XWNode.from_native({'count': 0}, immutable=True)
        
        # Create multiple versions
        v1 = original.set('count', 1)
        v2 = v1.set('count', 2)
        v3 = v2.set('count', 3)
        
        # All versions are independent
        assert original.to_native()['count'] == 0
        assert v1.to_native()['count'] == 1
        assert v2.to_native()['count'] == 2
        assert v3.to_native()['count'] == 3
    
    def test_to_native_preserves_data(self):
        """Test to_native() works with immutable nodes."""
        data = {'name': 'Alice', 'items': [1, 2, 3]}
        node = XWNode.from_native(data, immutable=True)
        
        # Modify
        node2 = node.set('name', 'Bob')
        
        # Both convert to native correctly
        native1 = node.to_native()
        native2 = node2.to_native()
        
        assert native1['name'] == 'Alice'
        assert native2['name'] == 'Bob'
        assert native1['items'] == [1, 2, 3]
        assert native2['items'] == [1, 2, 3]


@pytest.mark.xwnode_core
@pytest.mark.xwnode_performance
class TestCOWPerformance:
    """Core performance tests for COW (smoke tests)."""
    
    def test_cow_performance_smoke(self):
        """Smoke test that COW is reasonably fast."""
        import time
        
        # Create node with moderate data
        data = {f'key{i}': f'value{i}' for i in range(100)}
        node = XWNode.from_native(data, immutable=True)
        
        # Perform 100 mutations
        start = time.time()
        current = node
        for i in range(100):
            current = current.set(f'key{i}', f'new_value{i}')
        elapsed = time.time() - start
        
        # Should complete in < 1 second (very conservative)
        assert elapsed < 1.0, f"100 mutations took {elapsed:.3f}s, expected < 1.0s"
        
        # Original unchanged
        assert node.to_native()['key0'] == 'value0'
        
        # Final version has all changes
        assert current.to_native()['key99'] == 'new_value99'

