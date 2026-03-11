#!/usr/bin/env python3
"""
Script to verify base class inheritance for all node strategies.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import sys
from pathlib import Path
# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
from exonware.xwnode.defs import NodeMode
from exonware.xwnode.nodes.strategies.base import (
    ANodeStrategy,
    ANodeLinearStrategy,
    ANodeTreeStrategy,
    ANodeMatrixStrategy,
    ANodeGraphStrategy,
    AKeyValueStrategy
)
from exonware.xwnode.common.patterns.registry import StrategyRegistry


def get_expected_base_class(mode: NodeMode) -> type:
    """Determine expected base class for a node mode."""
    # Linear data structures
    linear_modes = {
        NodeMode.ARRAY_LIST,
        NodeMode.LINKED_LIST,
        NodeMode.STACK,
        NodeMode.QUEUE,
        NodeMode.DEQUE,
        NodeMode.PRIORITY_QUEUE,
        NodeMode.CIRCULAR_BUFFER,
    }
    # Matrix data structures
    matrix_modes = {
        NodeMode.SPARSE_MATRIX,
        NodeMode.BITMAP,
        NodeMode.BITSET_DYNAMIC,
        NodeMode.ROARING_BITMAP,
    }
    # Graph data structures
    graph_modes = {
        NodeMode.ADJACENCY_LIST,
        NodeMode.UNION_FIND,
    }
    # Tree data structures (default)
    # All other modes should use ANodeTreeStrategy
    if mode in linear_modes:
        return ANodeLinearStrategy
    elif mode in matrix_modes:
        return ANodeMatrixStrategy
    elif mode in graph_modes:
        return ANodeGraphStrategy
    else:
        return ANodeTreeStrategy  # Default for tree structures


def verify_strategy_inheritance():
    """Verify all node strategies inherit from correct base classes."""
    registry = StrategyRegistry()
    issues = []
    correct = []
    print("="*80)
    print("Node Strategy Inheritance Verification")
    print("="*80)
    print()
    # Get all registered node strategies
    all_modes = [mode for mode in NodeMode if mode != NodeMode.AUTO]
    for mode in sorted(all_modes, key=lambda x: x.name):
        try:
            strategy_class = registry.get_node_strategy_class(mode)
            if strategy_class is None:
                issues.append({
                    'mode': mode.name,
                    'issue': 'Strategy class not found in registry'
                })
                continue
            # Get actual base classes from MRO
            mro = strategy_class.__mro__
            actual_bases = [c for c in mro if issubclass(c, ANodeStrategy) and c != ANodeStrategy]
            # Get expected base class
            expected_base = get_expected_base_class(mode)
            # Check if strategy inherits from expected base
            if expected_base in mro:
                correct.append({
                    'mode': mode.name,
                    'strategy': strategy_class.__name__,
                    'expected': expected_base.__name__,
                    'actual': [c.__name__ for c in actual_bases]
                })
            else:
                issues.append({
                    'mode': mode.name,
                    'strategy': strategy_class.__name__,
                    'expected': expected_base.__name__,
                    'actual': [c.__name__ for c in actual_bases],
                    'issue': f'Does not inherit from {expected_base.__name__}'
                })
        except Exception as e:
            issues.append({
                'mode': mode.name,
                'issue': f'Error checking strategy: {str(e)}'
            })
    # Print results
    print(f"Total strategies: {len(all_modes)}")
    print(f"Correct: {len(correct)}")
    print(f"Issues: {len(issues)}")
    print()
    if issues:
        print("="*80)
        print("ISSUES FOUND:")
        print("="*80)
        for issue in issues:
            print(f"\n{issue['mode']}:")
            print(f"  Issue: {issue['issue']}")
            if 'strategy' in issue:
                print(f"  Strategy: {issue['strategy']}")
            if 'expected' in issue:
                print(f"  Expected base: {issue['expected']}")
            if 'actual' in issue:
                print(f"  Actual bases: {', '.join(issue['actual'])}")
    else:
        print("✅ All strategies inherit from correct base classes!")
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total: {len(all_modes)}")
    print(f"✅ Correct: {len(correct)}")
    print(f"❌ Issues: {len(issues)}")
    return issues
if __name__ == '__main__':
    issues = verify_strategy_inheritance()
    sys.exit(0 if len(issues) == 0 else 1)
