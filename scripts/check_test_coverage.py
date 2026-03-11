#!/usr/bin/env python3
"""
#exonware/xwnode/scripts/check_test_coverage.py
Check test coverage for xwnode strategies.
Compares defined strategies in defs.py with existing test files.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.1.0.1
Generation Date: 26-Jan-2025
"""

import sys
from pathlib import Path
from typing import Set, List, Tuple
# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from exonware.xwnode.defs import NodeMode, EdgeMode


def get_defined_strategies() -> Tuple[List[str], List[str]]:
    """Get all defined node and edge strategies from defs.py."""
    node_strategies = [mode.name for mode in NodeMode]
    edge_strategies = [mode.name for mode in EdgeMode]
    return node_strategies, edge_strategies


def get_existing_test_files() -> Tuple[Set[str], Set[str]]:
    """Get existing strategy test files."""
    tests_dir = Path(__file__).parent.parent / "tests"
    node_tests = set()
    edge_tests = set()
    # Search for test files
    for test_file in tests_dir.rglob("test_*_strategy.py"):
        name = test_file.stem.replace("test_", "").replace("_strategy", "")
        # Determine if node or edge based on path
        if "edge" in str(test_file).lower() or "edges" in str(test_file).lower():
            edge_tests.add(name.upper())
        else:
            node_tests.add(name.upper())
    return node_tests, edge_tests


def normalize_strategy_name(name: str) -> str:
    """Normalize strategy name for comparison."""
    # Convert to uppercase and handle variations
    name = name.upper()
    # Handle common variations
    name = name.replace("_", "")
    return name


def find_missing_tests() -> Tuple[List[str], List[str]]:
    """Find missing strategy test files."""
    defined_nodes, defined_edges = get_defined_strategies()
    existing_nodes, existing_edges = get_existing_test_files()
    # Normalize for comparison
    defined_nodes_norm = {normalize_strategy_name(n) for n in defined_nodes}
    defined_edges_norm = {normalize_strategy_name(e) for e in defined_edges}
    existing_nodes_norm = {normalize_strategy_name(n) for n in existing_nodes}
    existing_edges_norm = {normalize_strategy_name(e) for e in existing_edges}
    missing_nodes = [n for n in defined_nodes if normalize_strategy_name(n) not in existing_nodes_norm]
    missing_edges = [e for e in defined_edges if normalize_strategy_name(e) not in existing_edges_norm]
    return missing_nodes, missing_edges


def main():
    """Check test coverage."""
    print("=" * 60)
    print("XWNode Strategy Test Coverage Check")
    print("=" * 60)
    defined_nodes, defined_edges = get_defined_strategies()
    existing_nodes, existing_edges = get_existing_test_files()
    missing_nodes, missing_edges = find_missing_tests()
    print(f"\nDefined Strategies:")
    print(f"  Node Strategies: {len(defined_nodes)}")
    print(f"  Edge Strategies: {len(defined_edges)}")
    print(f"  Total: {len(defined_nodes) + len(defined_edges)}")
    print(f"\nExisting Test Files:")
    print(f"  Node Tests: {len(existing_nodes)}")
    print(f"  Edge Tests: {len(existing_edges)}")
    print(f"  Total: {len(existing_nodes) + len(existing_edges)}")
    print(f"\nMissing Test Files:")
    print(f"  Node Strategies: {len(missing_nodes)}")
    if missing_nodes:
        print(f"    Missing: {', '.join(missing_nodes[:10])}")
        if len(missing_nodes) > 10:
            print(f"    ... and {len(missing_nodes) - 10} more")
    print(f"  Edge Strategies: {len(missing_edges)}")
    if missing_edges:
        print(f"    Missing: {', '.join(missing_edges[:10])}")
        if len(missing_edges) > 10:
            print(f"    ... and {len(missing_edges) - 10} more")
    coverage_nodes = (len(existing_nodes) / len(defined_nodes) * 100) if defined_nodes else 0
    coverage_edges = (len(existing_edges) / len(defined_edges) * 100) if defined_edges else 0
    total_coverage = ((len(existing_nodes) + len(existing_edges)) / 
                     (len(defined_nodes) + len(defined_edges)) * 100) if (defined_nodes or defined_edges) else 0
    print(f"\nCoverage:")
    print(f"  Node Strategies: {coverage_nodes:.1f}%")
    print(f"  Edge Strategies: {coverage_edges:.1f}%")
    print(f"  Overall: {total_coverage:.1f}%")
    if missing_nodes or missing_edges:
        print(f"\nAction Required:")
        print(f"  Create {len(missing_nodes) + len(missing_edges)} missing test files")
        return 1
    else:
        print(f"\nAll strategies have test files!")
        return 0
if __name__ == "__main__":
    sys.exit(main())
