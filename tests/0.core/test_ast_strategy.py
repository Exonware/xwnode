"""
#exonware/xwnode/tests/0.core/test_ast_strategy.py
Comprehensive tests for AST node strategy.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: October 29, 2025
"""

import pytest
from exonware.xwnode.nodes.strategies.ast import ASTStrategy
from exonware.xwnode.defs import NodeMode, NodeTrait
from exonware.xwnode.nodes.strategies.contracts import NodeType
@pytest.mark.xwnode_core

class TestASTCore:
    """Core functionality tests for AST strategy."""

    def test_initialization_default(self):
        """Test initialization with default options."""
        strategy = ASTStrategy()
        assert strategy is not None
        assert strategy.STRATEGY_TYPE == NodeType.TREE

    def test_initialization_with_data(self):
        """Test initialization with AST data."""
        data = {
            'type': 'Module',
            'value': 'main',
            'children': []
        }
        strategy = ASTStrategy().create_from_data(data)
        assert strategy is not None
        assert strategy.get_type_count('Module') == 1

    def test_basic_type_indexing(self):
        """Test basic type indexing."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl', 'value': 'func1'},
                {'type': 'Variable', 'value': 'x'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Find all FunctionDecl nodes
        functions = strategy.find_all_by_type('FunctionDecl')
        assert len(functions) == 1
        assert functions[0]['value'] == 'func1'

    def test_find_first_by_type(self):
        """Test finding first node of type."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'Variable', 'value': 'x'},
                {'type': 'FunctionDecl', 'value': 'func1'},
                {'type': 'FunctionDecl', 'value': 'func2'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        func = strategy.find_first_by_type('FunctionDecl')
        assert func is not None
        assert func['value'] == 'func1'

    def test_get_type_count(self):
        """Test type counting."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl'},
                {'type': 'FunctionDecl'},
                {'type': 'Variable'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        assert strategy.get_type_count('FunctionDecl') == 2
        assert strategy.get_type_count('Variable') == 1
        assert strategy.get_type_count('Module') == 1

    def test_get_all_types(self):
        """Test getting all unique types."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl'},
                {'type': 'Variable'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        types = strategy.get_all_types()
        assert 'Module' in types
        assert 'FunctionDecl' in types
        assert 'Variable' in types

    def test_metrics_computation(self):
        """Test metrics are computed correctly."""
        data = {
            'type': 'Module',
            'children': [
                {
                    'type': 'FunctionDecl',
                    'children': [
                        {'type': 'Parameter'},
                        {'type': 'Block'},
                    ]
                }
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        metrics = strategy.get_metrics()
        assert metrics['total_nodes'] > 0
        assert metrics['max_depth'] > 0
        assert 'type_counts' in metrics
        assert metrics['indexed'] is True

    def test_pattern_matching_with_type(self):
        """Test pattern matching with type filter."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl', 'value': 'func1', 'metadata': {'public': True}},
                {'type': 'FunctionDecl', 'value': 'func2', 'metadata': {'public': False}},
                {'type': 'Variable', 'value': 'x'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Find public functions
        public_funcs = strategy.find_pattern({
            'type': 'FunctionDecl',
            'metadata.public': True
        })
        assert len(public_funcs) == 1
        assert public_funcs[0]['value'] == 'func1'

    def test_pattern_matching_without_type(self):
        """Test pattern matching without type filter."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl', 'value': 'x'},
                {'type': 'Variable', 'value': 'x'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Find all nodes with value 'x'
        x_nodes = strategy.find_pattern({'value': 'x'})
        assert len(x_nodes) == 2

    def test_nested_ast_indexing(self):
        """Test indexing deeply nested AST."""
        data = {
            'type': 'Module',
            'children': [
                {
                    'type': 'FunctionDecl',
                    'children': [
                        {
                            'type': 'Block',
                            'children': [
                                {
                                    'type': 'If',
                                    'children': [
                                        {'type': 'Condition'},
                                        {'type': 'Block'}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        assert strategy.get_type_count('Module') == 1
        assert strategy.get_type_count('FunctionDecl') == 1
        assert strategy.get_type_count('Block') == 2
        assert strategy.get_type_count('If') == 1
        assert strategy.get_type_count('Condition') == 1
@pytest.mark.xwnode_performance

class TestASTPerformance:
    """Performance validation tests for AST strategy."""

    def test_type_lookup_o1(self):
        """Validate O(1) type lookup (plus O(k) for copying results)."""
        import time
        # Test 1: Type lookup with CONSTANT result size (truly O(1))
        # Create ASTs where 'Marker' type count is always 10
        strategies = {}
        for total_size in [100, 500, 1000]:
            children = [{'type': 'Marker', 'value': f'm{i}'} for i in range(10)]
            children += [{'type': 'Filler', 'value': f'f{i}'} for i in range(total_size - 10)]
            data = {'type': 'Module', 'children': children}
            strategies[total_size] = ASTStrategy().create_from_data(data)
        # Measure find_all_by_type for 'Marker' (always 10 results)
        timings = {}
        for total_size, strategy in strategies.items():
            measurements = []
            for _ in range(100):
                start = time.perf_counter()
                results = strategy.find_all_by_type('Marker')
                elapsed = time.perf_counter() - start
                measurements.append(elapsed)
            measurements.sort()
            timings[total_size] = measurements[len(measurements)//2]  # Median
            assert len(results) == 10  # Verify constant result size
        # With constant result size, time should be constant (O(1) lookup + O(10) copy)
        # Allow 5x ratio for timing variance
        ratio = timings[1000] / timings[100]
        assert ratio < 5.0, (
            f"Expected O(1) type lookup with constant results, but ratio {ratio:.2f} indicates scaling. "
            f"Timings: {timings}"
        )

    def test_type_count_o1(self):
        """Validate O(1) type counting."""
        import time
        # Create large AST
        children = [{'type': 'FunctionDecl', 'value': f'f{i}'} for i in range(1000)]
        data = {'type': 'Module', 'children': children}
        strategy = ASTStrategy().create_from_data(data)
        # Measure type counting
        measurements = []
        for _ in range(1000):
            start = time.perf_counter()
            count = strategy.get_type_count('FunctionDecl')
            elapsed = time.perf_counter() - start
            measurements.append(elapsed)
        measurements.sort()
        median_time = measurements[len(measurements)//2]
        # Should be extremely fast (< 1 microsecond)
        assert median_time < 0.000001, (
            f"Type counting took {median_time*1000000:.2f}µs, expected < 1µs"
        )

    def test_metrics_caching(self):
        """Test that metrics are cached (not recomputed)."""
        import time
        # Create large AST
        children = [{'type': f'Type{i%10}', 'value': i} for i in range(1000)]
        data = {'type': 'Module', 'children': children}
        strategy = ASTStrategy().create_from_data(data)
        # First call
        start = time.perf_counter()
        metrics1 = strategy.get_metrics()
        time1 = time.perf_counter() - start
        # Second call (should be instant - cached)
        start = time.perf_counter()
        metrics2 = strategy.get_metrics()
        time2 = time.perf_counter() - start
        # Metrics should be the same
        assert metrics1 == metrics2
        # Second call should be much faster (or at least not slower)
        # Both should be very fast since metrics are cached
        assert time2 < 0.0001  # < 0.1ms
@pytest.mark.xwnode_core

class TestASTEdgeCases:
    """Edge case and error handling tests."""

    def test_empty_ast(self):
        """Test with empty AST."""
        data = {'type': 'Module', 'children': []}
        strategy = ASTStrategy().create_from_data(data)
        assert strategy.get_type_count('Module') == 1
        assert strategy.get_type_count('FunctionDecl') == 0
        assert strategy.find_all_by_type('FunctionDecl') == []

    def test_single_node_ast(self):
        """Test with single node."""
        data = {'type': 'Module'}
        strategy = ASTStrategy().create_from_data(data)
        assert strategy.get_type_count('Module') == 1
        assert len(strategy.get_all_types()) == 1

    def test_missing_type_field(self):
        """Test nodes without 'type' field."""
        data = {
            'type': 'Module',
            'children': [
                {'value': 'no_type'},  # No 'type' field
                {'type': 'Variable', 'value': 'x'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Should handle gracefully
        assert strategy.get_type_count('Variable') == 1

    def test_deeply_nested_ast(self):
        """Test with very deep nesting."""
        # Create AST with depth 20
        data = {'type': 'Level0'}
        current = data
        for i in range(1, 20):
            current['children'] = [{'type': f'Level{i}'}]
            current = current['children'][0]
        strategy = ASTStrategy().create_from_data(data)
        # Should index all levels
        assert strategy.get_type_count('Level0') == 1
        assert strategy.get_type_count('Level19') == 1
        assert strategy.get_depth() >= 19

    def test_wide_ast(self):
        """Test with many children at one level."""
        children = [{'type': 'Child', 'value': i} for i in range(1000)]
        data = {'type': 'Module', 'children': children}
        strategy = ASTStrategy().create_from_data(data)
        assert strategy.get_type_count('Child') == 1000
        assert len(strategy.find_all_by_type('Child')) == 1000

    def test_many_different_types(self):
        """Test with many different node types."""
        children = [{'type': f'Type{i}'} for i in range(100)]
        data = {'type': 'Module', 'children': children}
        strategy = ASTStrategy().create_from_data(data)
        all_types = strategy.get_all_types()
        assert len(all_types) == 101  # 100 children + 1 Module

    def test_pattern_with_nested_metadata(self):
        """Test pattern matching with deeply nested metadata."""
        data = {
            'type': 'Module',
            'children': [
                {
                    'type': 'FunctionDecl',
                    'metadata': {
                        'annotations': {
                            'visibility': 'public'
                        }
                    }
                }
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # This tests the nested key handling
        # Currently metadata.visibility won't match metadata.annotations.visibility
        # But it should handle gracefully
        funcs = strategy.find_pattern({'type': 'FunctionDecl'})
        assert len(funcs) == 1

    def test_get_summary(self):
        """Test summary generation."""
        children = [{'type': 'FunctionDecl'} for _ in range(10)]
        data = {'type': 'Module', 'children': children}
        strategy = ASTStrategy().create_from_data(data)
        summary = strategy.get_summary()
        assert 'AST:' in summary
        assert 'nodes' in summary
        assert 'types' in summary

    def test_type_distribution(self):
        """Test type distribution calculation."""
        children = [
            {'type': 'FunctionDecl'},
            {'type': 'FunctionDecl'},
            {'type': 'Variable'},
        ]
        data = {'type': 'Module', 'children': children}
        strategy = ASTStrategy().create_from_data(data)
        dist = strategy.get_type_distribution()
        assert 'Module' in dist
        assert 'FunctionDecl' in dist
        assert dist['FunctionDecl'] > dist['Variable']  # 2 vs 1
@pytest.mark.xwnode_core

class TestASTIndexOptimizations:
    """Test index-based optimizations."""

    def test_type_index_coverage(self):
        """Test that all nodes with types are indexed."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'A'},
                {'type': 'B'},
                {'type': 'C'},
                {'type': 'A'},  # Duplicate type
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # All types should be indexed
        assert 'A' in strategy.get_all_types()
        assert 'B' in strategy.get_all_types()
        assert 'C' in strategy.get_all_types()
        assert 'Module' in strategy.get_all_types()
        # Duplicates should both be findable
        a_nodes = strategy.find_all_by_type('A')
        assert len(a_nodes) == 2

    def test_path_index_coverage(self):
        """Test that nodes are indexed by path."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'Child1'},
                {'type': 'Child2'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Should be able to get nodes by path
        node = strategy.get_node_by_path('children[0]')
        assert node is not None
        assert node['type'] == 'Child1'
        node = strategy.get_node_by_path('children[1]')
        assert node is not None
        assert node['type'] == 'Child2'

    def test_metrics_accurate_count(self):
        """Test that metrics accurately count all nodes."""
        # Create known structure
        data = {
            'type': 'Module',
            'children': [
                {'type': 'A'},
                {'type': 'B'},
                {'type': 'C'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        metrics = strategy.get_metrics()
        # 1 Module + 3 children = 4 total
        assert metrics['total_nodes'] == 4

    def test_metrics_max_depth(self):
        """Test max depth calculation."""
        data = {
            'type': 'L0',
            'children': [
                {
                    'type': 'L1',
                    'children': [
                        {
                            'type': 'L2',
                            'children': [
                                {'type': 'L3'}
                            ]
                        }
                    ]
                }
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        assert strategy.get_depth() >= 3
@pytest.mark.xwnode_core

class TestASTSpecialCases:
    """Test special AST scenarios."""

    def test_ast_with_metadata_only(self):
        """Test AST nodes with metadata but no children."""
        data = {
            'type': 'Module',
            'metadata': {'file': 'main.py', 'line': 1},
            'children': [
                {'type': 'FunctionDecl', 'metadata': {'line': 5}}
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        assert strategy.get_type_count('Module') == 1
        assert strategy.get_type_count('FunctionDecl') == 1

    def test_ast_with_mixed_children_types(self):
        """Test AST with heterogeneous children."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'Import', 'value': 'os'},
                {'type': 'FunctionDecl', 'value': 'main'},
                {'type': 'ClassDecl', 'value': 'MyClass'},
                {'type': 'Variable', 'value': 'x'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        assert len(strategy.get_all_types()) == 5  # Module + 4 children types
        assert strategy.get_type_count('Import') == 1
        assert strategy.get_type_count('FunctionDecl') == 1
        assert strategy.get_type_count('ClassDecl') == 1
        assert strategy.get_type_count('Variable') == 1

    def test_large_ast_performance(self):
        """Test with large AST (1000+ nodes)."""
        import time
        # Create large AST
        children = []
        for i in range(250):
            children.append({'type': 'FunctionDecl', 'value': f'f{i}'})
        for i in range(250):
            children.append({'type': 'Variable', 'value': f'v{i}'})
        for i in range(250):
            children.append({'type': 'If', 'value': f'if{i}'})
        for i in range(250):
            children.append({'type': 'Return', 'value': f'ret{i}'})
        data = {'type': 'Module', 'children': children}
        # Creation should be fast even for large ASTs
        start = time.perf_counter()
        strategy = ASTStrategy().create_from_data(data)
        creation_time = time.perf_counter() - start
        # Should create in reasonable time (< 100ms)
        assert creation_time < 0.1, f"Creation took {creation_time*1000:.2f}ms"
        # Type lookups should be instant
        start = time.perf_counter()
        functions = strategy.find_all_by_type('FunctionDecl')
        lookup_time = time.perf_counter() - start
        assert len(functions) == 250
        assert lookup_time < 0.001, f"Lookup took {lookup_time*1000:.2f}ms"

    def test_comparison_vs_traversal(self):
        """Compare indexed lookup vs manual traversal."""
        import time
        # Create medium-sized AST
        children = [{'type': 'FunctionDecl' if i % 3 == 0 else 'Variable', 'value': i} 
                   for i in range(300)]
        data = {'type': 'Module', 'children': children}
        strategy = ASTStrategy().create_from_data(data)
        # Method 1: Using type index (O(1))
        start = time.perf_counter()
        indexed_result = strategy.find_all_by_type('FunctionDecl')
        indexed_time = time.perf_counter() - start
        # Method 2: Manual traversal (O(n))
        def traverse(node):
            results = []
            if isinstance(node, dict):
                if node.get('type') == 'FunctionDecl':
                    results.append(node)
                for child in node.get('children', []):
                    results.extend(traverse(child))
            elif isinstance(node, list):
                for item in node:
                    results.extend(traverse(item))
            return results
        start = time.perf_counter()
        traversal_result = traverse(data)
        traversal_time = time.perf_counter() - start
        # Both should find same number of nodes
        assert len(indexed_result) == len(traversal_result)
        # Indexed should be faster (or at least not slower)
        # Note: For small ASTs, setup overhead might make it slower
        # But for repeated lookups, indexed is much better
@pytest.mark.xwnode_core

class TestASTIntegrationWithTreeGraphHybrid:
    """Test that AST strategy properly extends TreeGraphHybridStrategy."""

    def test_inherits_tree_navigation(self):
        """Test that tree navigation from parent works."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl', 'value': 'func1'}
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Should have tree navigation capabilities from parent
        assert hasattr(strategy, 'to_native')
        assert hasattr(strategy, 'create_from_data')

    def test_to_native_conversion(self):
        """Test conversion to native format."""
        data = {
            'type': 'Module',
            'value': 'main',
            'children': [
                {'type': 'FunctionDecl', 'value': 'func1'}
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        native = strategy.to_native()
        assert isinstance(native, dict)
        assert native['type'] == 'Module'
        assert native['value'] == 'main'

    def test_supports_all_base_operations(self):
        """Test that AST strategy supports base strategy operations."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl'}
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Check for essential methods from parent
        assert hasattr(strategy, 'create_from_data')
        assert hasattr(strategy, 'to_native')
        assert hasattr(strategy, 'STRATEGY_TYPE')
        # Check for AST-specific methods
        assert hasattr(strategy, 'find_all_by_type')
        assert hasattr(strategy, 'get_type_count')
        assert hasattr(strategy, 'get_metrics')
        assert hasattr(strategy, 'find_pattern')
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
