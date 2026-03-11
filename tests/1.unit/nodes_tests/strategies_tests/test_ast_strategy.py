#!/usr/bin/env python3
"""
Test AST Strategy
Company: eXonware.com
Author: eXonware Backend Team
Date: October 29, 2025
"""

import pytest
from exonware.xwnode.nodes.strategies.ast import ASTStrategy


class TestASTStrategyBasics:
    """Test basic AST strategy functionality."""

    def test_create_simple_ast(self):
        """Test creating simple AST."""
        data = {
            'type': 'Module',
            'value': 'main',
            'children': []
        }
        strategy = ASTStrategy().create_from_data(data)
        assert strategy is not None

    def test_create_ast_with_children(self):
        """Test creating AST with children."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl', 'value': 'func1'},
                {'type': 'Variable', 'value': 'x'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        assert strategy is not None


class TestTypeIndexing:
    """Test type-based indexing optimization."""

    def test_find_all_by_type(self):
        """Test O(1) find_all_by_type."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl', 'value': 'func1'},
                {'type': 'FunctionDecl', 'value': 'func2'},
                {'type': 'Variable', 'value': 'x'},
                {'type': 'FunctionDecl', 'value': 'func3'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Should return all 3 functions in O(1)
        functions = strategy.find_all_by_type('FunctionDecl')
        assert len(functions) == 3
        assert all(f['type'] == 'FunctionDecl' for f in functions)

    def test_find_first_by_type(self):
        """Test O(1) find_first_by_type."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'Variable', 'value': 'x'},
                {'type': 'FunctionDecl', 'value': 'func1'},
                {'type': 'FunctionDecl', 'value': 'func2'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Should return first function in O(1)
        func = strategy.find_first_by_type('FunctionDecl')
        assert func is not None
        assert func['type'] == 'FunctionDecl'
        assert func['value'] == 'func1'

    def test_find_nonexistent_type(self):
        """Test finding non-existent type."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'Variable', 'value': 'x'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        functions = strategy.find_all_by_type('FunctionDecl')
        assert functions == []
        func = strategy.find_first_by_type('FunctionDecl')
        assert func is None

    def test_get_type_count(self):
        """Test O(1) type counting."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl', 'value': 'f1'},
                {'type': 'FunctionDecl', 'value': 'f2'},
                {'type': 'Variable', 'value': 'x'},
                {'type': 'Variable', 'value': 'y'},
                {'type': 'Variable', 'value': 'z'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        assert strategy.get_type_count('FunctionDecl') == 2
        assert strategy.get_type_count('Variable') == 3
        assert strategy.get_type_count('Module') == 1  # Root
        assert strategy.get_type_count('NonExistent') == 0

    def test_get_all_types(self):
        """Test getting all unique types."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl'},
                {'type': 'Variable'},
                {'type': 'If'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        types = strategy.get_all_types()
        assert 'Module' in types
        assert 'FunctionDecl' in types
        assert 'Variable' in types
        assert 'If' in types
        assert len(types) == 4


class TestMetrics:
    """Test pre-computed metrics."""

    def test_get_metrics(self):
        """Test getting AST metrics."""
        data = {
            'type': 'Module',
            'children': [
                {
                    'type': 'FunctionDecl',
                    'children': [
                        {'type': 'Parameter', 'value': 'x'},
                        {
                            'type': 'Block',
                            'children': [
                                {'type': 'Return', 'value': 'x'}
                            ]
                        }
                    ]
                }
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        metrics = strategy.get_metrics()
        assert 'total_nodes' in metrics
        assert 'max_depth' in metrics
        assert 'type_counts' in metrics
        assert metrics['total_nodes'] > 0
        assert metrics['indexed'] is True

    def test_get_depth(self):
        """Test max depth calculation."""
        data = {
            'type': 'Module',
            'children': [
                {
                    'type': 'FunctionDecl',
                    'children': [
                        {
                            'type': 'Block',
                            'children': [
                                {'type': 'If'}  # Depth 3
                            ]
                        }
                    ]
                }
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        assert strategy.get_depth() >= 3

    def test_get_summary(self):
        """Test summary string generation."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl'},
                {'type': 'Variable'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        summary = strategy.get_summary()
        assert 'AST:' in summary
        assert 'nodes' in summary
        assert 'types' in summary
        assert 'depth' in summary

    def test_get_type_distribution(self):
        """Test type distribution percentages."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl'},
                {'type': 'FunctionDecl'},
                {'type': 'Variable'},
                {'type': 'Variable'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        dist = strategy.get_type_distribution()
        assert 'Module' in dist
        assert 'FunctionDecl' in dist
        assert 'Variable' in dist
        # Should have percentages
        total_percent = sum(dist.values())
        assert 99 < total_percent <= 100  # Allow floating point rounding


class TestPatternMatching:
    """Test pattern matching optimization."""

    def test_find_pattern_with_type(self):
        """Test pattern matching with type filter."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl', 'value': 'public_func', 'metadata': {'visibility': 'public'}},
                {'type': 'FunctionDecl', 'value': 'private_func', 'metadata': {'visibility': 'private'}},
                {'type': 'Variable', 'value': 'x'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Find public functions
        public_funcs = strategy.find_pattern({
            'type': 'FunctionDecl',
            'metadata.visibility': 'public'
        })
        assert len(public_funcs) == 1
        assert public_funcs[0]['value'] == 'public_func'

    def test_find_pattern_without_type(self):
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

    def test_find_pattern_nested_key(self):
        """Test pattern matching with nested keys."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl', 'metadata': {'line': 10}},
                {'type': 'FunctionDecl', 'metadata': {'line': 20}},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Find functions at line 10
        funcs = strategy.find_pattern({
            'type': 'FunctionDecl',
            'metadata.line': 10
        })
        assert len(funcs) == 1
        assert funcs[0]['metadata']['line'] == 10


class TestPathIndex:
    """Test path-based indexing."""

    def test_get_node_by_path(self):
        """Test O(1) node lookup by path."""
        data = {
            'type': 'Module',
            'children': [
                {'type': 'FunctionDecl', 'value': 'func1'},
                {'type': 'Variable', 'value': 'x'},
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Get first child by path
        node = strategy.get_node_by_path('children[0]')
        assert node is not None
        assert node['type'] == 'FunctionDecl'

    def test_get_nonexistent_path(self):
        """Test getting node at non-existent path."""
        data = {
            'type': 'Module',
            'children': []
        }
        strategy = ASTStrategy().create_from_data(data)
        node = strategy.get_node_by_path('nonexistent.path')
        assert node is None


class TestComplexAST:
    """Test with more complex, realistic ASTs."""

    def test_large_nested_ast(self):
        """Test with deeply nested AST."""
        data = {
            'type': 'Module',
            'children': [
                {
                    'type': 'FunctionDecl',
                    'value': 'main',
                    'children': [
                        {'type': 'Parameter', 'value': 'x'},
                        {
                            'type': 'Block',
                            'children': [
                                {
                                    'type': 'If',
                                    'children': [
                                        {'type': 'Condition'},
                                        {
                                            'type': 'Block',
                                            'children': [
                                                {'type': 'Return'}
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        strategy = ASTStrategy().create_from_data(data)
        # Verify all types are indexed
        assert strategy.get_type_count('Module') == 1
        assert strategy.get_type_count('FunctionDecl') == 1
        assert strategy.get_type_count('Parameter') == 1
        assert strategy.get_type_count('Block') == 2
        assert strategy.get_type_count('If') == 1
        assert strategy.get_type_count('Condition') == 1
        assert strategy.get_type_count('Return') == 1
        # Verify metrics
        metrics = strategy.get_metrics()
        assert metrics['total_nodes'] >= 7  # At least 7 nodes (may index metadata nodes too)
        assert metrics['max_depth'] >= 4

    def test_multiple_same_type_nodes(self):
        """Test with many nodes of same type."""
        children = [{'type': 'Variable', 'value': f'var{i}'} for i in range(100)]
        data = {
            'type': 'Module',
            'children': children
        }
        strategy = ASTStrategy().create_from_data(data)
        # Should find all 100 variables instantly
        variables = strategy.find_all_by_type('Variable')
        assert len(variables) == 100
        # Count should match
        assert strategy.get_type_count('Variable') == 100
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
