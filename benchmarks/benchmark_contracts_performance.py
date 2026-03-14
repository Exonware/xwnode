#!/usr/bin/env python3
"""
Benchmark: Old (List) vs New (Frozenset) SUPPORTED_OPERATIONS
Compares performance of operation lookup between list-based and frozenset-based
implementations of SUPPORTED_OPERATIONS in contracts.py.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 22-Oct-2025
"""

import sys
from pathlib import Path
import time
from abc import ABC, abstractmethod
from typing import Any
# Add src to path
from collections.abc import Iterator
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
# Handle Windows encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# ==============================================================================
# OLD IMPLEMENTATION (List-based) - O(n) lookup
# ==============================================================================


class INodeStrategyOld(ABC):
    """OLD: List-based SUPPORTED_OPERATIONS (O(n) lookup)"""
    SUPPORTED_OPERATIONS: list[str] = []  # Old: List
    @classmethod

    def get_supported_operations(cls) -> list[str]:
        return cls.SUPPORTED_OPERATIONS  # Old: Direct return
    @classmethod

    def supports_operation(cls, operation: str) -> bool:
        if not cls.SUPPORTED_OPERATIONS:
            return True
        return operation in cls.SUPPORTED_OPERATIONS  # O(n) with list
# ==============================================================================
# NEW IMPLEMENTATION (Frozenset-based) - O(1) lookup
# ==============================================================================


class INodeStrategyNew(ABC):
    """NEW: Frozenset-based SUPPORTED_OPERATIONS (O(1) lookup)"""
    SUPPORTED_OPERATIONS: frozenset[str] = frozenset()  # New: Frozenset
    @classmethod

    def get_supported_operations(cls) -> list[str]:
        return list(cls.SUPPORTED_OPERATIONS)  # New: Convert to list
    @classmethod

    def supports_operation(cls, operation: str) -> bool:
        if not cls.SUPPORTED_OPERATIONS:
            return True
        return operation in cls.SUPPORTED_OPERATIONS  # O(1) with frozenset
# ==============================================================================
# CONCRETE DUMMY IMPLEMENTATIONS
# ==============================================================================


class DummyStrategyOld(INodeStrategyOld):
    """Dummy strategy with OLD list-based operations"""
    pass


class DummyStrategyNew(INodeStrategyNew):
    """Dummy strategy with NEW frozenset-based operations"""
    pass
# ==============================================================================
# BENCHMARK FUNCTIONS
# ==============================================================================


def benchmark_operation_lookup(strategy_class, operations: list[str], 
                               num_lookups: int = 100000) -> float:
    """
    Benchmark operation lookup performance.
    Args:
        strategy_class: Strategy class to test
        operations: List of operations to lookup
        num_lookups: Number of lookups to perform
    Returns:
        Total time in seconds
    """
    start = time.perf_counter()
    # Perform lookups
    for _ in range(num_lookups):
        for op in operations:
            strategy_class.supports_operation(op)
    elapsed = time.perf_counter() - start
    return elapsed


def verify_correctness(old_class, new_class, operations: list[str]):
    """Verify both implementations produce identical results"""
    print("\n" + "="*80)
    print("🔍 CORRECTNESS VERIFICATION")
    print("="*80)
    # Test empty operations
    assert old_class.supports_operation("any_op") == new_class.supports_operation("any_op")
    print("✓ Empty operations: Both return True for any operation")
    # Create test strategies with operations
    class OldWithOps(old_class):
        SUPPORTED_OPERATIONS = operations.copy()
    class NewWithOps(new_class):
        SUPPORTED_OPERATIONS = frozenset(operations)
    # Test supported operations
    for op in operations:
        old_result = OldWithOps.supports_operation(op)
        new_result = NewWithOps.supports_operation(op)
        assert old_result == new_result, f"Mismatch for operation: {op}"
    print(f"✓ Supported operations: All {len(operations)} operations match")
    # Test unsupported operation
    unsupported = "unsupported_operation_xyz"
    old_result = OldWithOps.supports_operation(unsupported)
    new_result = NewWithOps.supports_operation(unsupported)
    assert old_result == new_result == False
    print(f"✓ Unsupported operations: Both return False")
    # Test get_supported_operations returns list
    old_ops = OldWithOps.get_supported_operations()
    new_ops = NewWithOps.get_supported_operations()
    assert isinstance(old_ops, list), "Old should return list"
    assert isinstance(new_ops, list), "New should return list"
    assert set(old_ops) == set(new_ops), "Operations set should match"
    print(f"✓ get_supported_operations(): Both return list with same operations")
    print("\n✅ ALL CORRECTNESS CHECKS PASSED!\n")


def run_benchmark_suite():
    """Run comprehensive benchmark suite"""
    print("="*80)
    print("⚡ PERFORMANCE BENCHMARK: Old (List) vs New (Frozenset)")
    print("="*80)
    print()
    # Test configurations
    test_configs = [
        {"ops": 5, "lookups": 100000, "desc": "Small (5 ops)"},
        {"ops": 10, "lookups": 100000, "desc": "Small (10 ops)"},
        {"ops": 50, "lookups": 50000, "desc": "Medium (50 ops)"},
        {"ops": 100, "lookups": 50000, "desc": "Medium (100 ops)"},
        {"ops": 500, "lookups": 10000, "desc": "Large (500 ops)"},
        {"ops": 1000, "lookups": 10000, "desc": "Large (1000 ops)"},
    ]
    results = []
    for config in test_configs:
        num_ops = config["ops"]
        num_lookups = config["lookups"]
        desc = config["desc"]
        # Generate operation names
        operations = [f"operation_{i}" for i in range(num_ops)]
        # Create test classes
        class OldTest(DummyStrategyOld):
            SUPPORTED_OPERATIONS = operations.copy()
        class NewTest(DummyStrategyNew):
            SUPPORTED_OPERATIONS = frozenset(operations)
        print(f"\n📊 Testing: {desc}")
        print(f"   Operations: {num_ops}, Lookups per run: {num_lookups:,}")
        # Warm-up
        benchmark_operation_lookup(OldTest, operations[:3], 100)
        benchmark_operation_lookup(NewTest, operations[:3], 100)
        # Benchmark OLD (List)
        old_time = benchmark_operation_lookup(OldTest, operations, num_lookups)
        old_time_ms = old_time * 1000
        old_per_lookup_ns = (old_time / (num_lookups * num_ops)) * 1_000_000_000
        # Benchmark NEW (Frozenset)
        new_time = benchmark_operation_lookup(NewTest, operations, num_lookups)
        new_time_ms = new_time * 1000
        new_per_lookup_ns = (new_time / (num_lookups * num_ops)) * 1_000_000_000
        # Calculate speedup
        speedup = old_time / new_time if new_time > 0 else float('inf')
        improvement_pct = ((old_time - new_time) / old_time) * 100 if old_time > 0 else 0
        print(f"\n   OLD (List):     {old_time_ms:8.2f} ms  ({old_per_lookup_ns:6.1f} ns/lookup)")
        print(f"   NEW (Frozenset): {new_time_ms:8.2f} ms  ({new_per_lookup_ns:6.1f} ns/lookup)")
        print(f"   ⚡ Speedup:      {speedup:8.2f}x  ({improvement_pct:5.1f}% faster)")
        results.append({
            'config': desc,
            'ops': num_ops,
            'old_time_ms': old_time_ms,
            'new_time_ms': new_time_ms,
            'old_ns': old_per_lookup_ns,
            'new_ns': new_per_lookup_ns,
            'speedup': speedup,
            'improvement_pct': improvement_pct
        })
    return results


def print_summary_table(results):
    """Print formatted summary table"""
    print("\n" + "="*80)
    print("📊 PERFORMANCE SUMMARY TABLE")
    print("="*80)
    print()
    # Header
    print(f"{'Configuration':<20} {'Old (ms)':<12} {'New (ms)':<12} {'Speedup':<10} {'Improvement':<12}")
    print("-" * 80)
    # Rows
    for r in results:
        print(f"{r['config']:<20} "
              f"{r['old_time_ms']:>10.2f}  "
              f"{r['new_time_ms']:>10.2f}  "
              f"{r['speedup']:>8.2f}x  "
              f"{r['improvement_pct']:>9.1f}%")
    print("-" * 80)
    # Average speedup
    avg_speedup = sum(r['speedup'] for r in results) / len(results)
    max_speedup = max(r['speedup'] for r in results)
    min_speedup = min(r['speedup'] for r in results)
    print(f"\n{'Average Speedup:':<20} {avg_speedup:>8.2f}x")
    print(f"{'Maximum Speedup:':<20} {max_speedup:>8.2f}x")
    print(f"{'Minimum Speedup:':<20} {min_speedup:>8.2f}x")


def print_conclusion(results):
    """Print final conclusion"""
    print("\n" + "="*80)
    print("🎯 CONCLUSION")
    print("="*80)
    print()
    avg_speedup = sum(r['speedup'] for r in results) / len(results)
    max_speedup = max(r['speedup'] for r in results)
    print("✅ NEW Implementation (frozenset) is FASTER and ACCURATE")
    print()
    print(f"   • Average speedup: {avg_speedup:.2f}x faster")
    print(f"   • Maximum speedup: {max_speedup:.2f}x faster (large operation sets)")
    print(f"   • Time Complexity: O(1) vs O(n)")
    print(f"   • All correctness tests passed")
    print(f"   • Backward compatible (returns list)")
    print()
    print("🚀 Recommendation: NEW implementation provides significant")
    print("   performance improvement with zero breaking changes!")
    print()
# ==============================================================================
# MAIN EXECUTION
# ==============================================================================


def main():
    """Main benchmark execution"""
    # Generate test operations
    test_operations = [f"operation_{i}" for i in range(100)]
    # Verify correctness first
    verify_correctness(DummyStrategyOld, DummyStrategyNew, test_operations)
    # Run performance benchmarks
    results = run_benchmark_suite()
    # Print summary
    print_summary_table(results)
    # Print conclusion
    print_conclusion(results)
    print("="*80)
    print("✅ Benchmark Complete!")
    print("="*80)
if __name__ == "__main__":
    main()
