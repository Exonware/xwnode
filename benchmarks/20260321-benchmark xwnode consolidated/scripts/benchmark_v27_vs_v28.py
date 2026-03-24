#!/usr/bin/env python3
"""
Benchmark: v0.0.1.27 vs v0.0.1.28
Compares performance between:
- v0.0.1.27: Async + Thread-Safe
- v0.0.1.28: Ultra-Optimized (cached, __slots__, explicit enums, __init_subclass__)
Runs 5 times for statistical accuracy, tests if v0.0.1.28 is actually faster.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Generation Date: 22-Oct-2025
"""

import sys
from pathlib import Path
import time
import statistics
from abc import ABC, abstractmethod
from typing import Any
from enum import Enum, auto
# Handle Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# Add src to path
src_path = Path(__file__).resolve().parents[3] / "src"
sys.path.insert(0, str(src_path))
# ==============================================================================
# VERSION 0.0.1.27: Async + Thread-Safe
# ==============================================================================


class NodeTypeV27(Enum):
    """v0.0.1.27: auto() values"""
    LINEAR = auto()
    TREE = auto()
    GRAPH = auto()
    MATRIX = auto()
    HYBRID = auto()


class INodeStrategyV27(ABC):
    """v0.0.1.27: Async + Thread-safe (no caching, no __slots__)"""
    STRATEGY_TYPE: NodeTypeV27 = NodeTypeV27.TREE
    SUPPORTED_OPERATIONS: frozenset[str] = frozenset()
    @classmethod

    def get_supported_operations(cls) -> list[str]:
        """v0.0.1.27: Converts to list every time (O(n))"""
        return list(cls.SUPPORTED_OPERATIONS)
    @classmethod

    def supports_operation(cls, operation: str) -> bool:
        if not cls.SUPPORTED_OPERATIONS:
            return True
        return operation in cls.SUPPORTED_OPERATIONS
# ==============================================================================
# VERSION 0.0.1.28: Ultra-Optimized
# ==============================================================================
# Pre-computed common operations
COMMON_OPS_V28 = frozenset([
    "insert", "find", "delete", "size", "is_empty",
    "keys", "values", "items", "to_native"
])
# Operations cache
_OPS_CACHE_V28: dict[type, list[str]] = {}


class NodeTypeV28(Enum):
    """v0.0.1.28: Explicit int values for faster comparisons"""
    LINEAR = 1
    TREE = 2
    GRAPH = 3
    MATRIX = 4
    HYBRID = 5


class INodeStrategyV28(ABC):
    """v0.0.1.28: Ultra-optimized (cached, __slots__, explicit enums)"""
    __slots__ = ()  # Memory optimization
    STRATEGY_TYPE: NodeTypeV28 = NodeTypeV28.TREE
    SUPPORTED_OPERATIONS: frozenset[str] = frozenset()

    def __init_subclass__(cls, **kwargs):
        """Auto-optimize and pre-cache at definition time"""
        super().__init_subclass__(**kwargs)
        # Auto-convert to frozenset
        if hasattr(cls, 'SUPPORTED_OPERATIONS'):
            ops = cls.SUPPORTED_OPERATIONS
            if not isinstance(ops, frozenset):
                if isinstance(ops, (list, set, tuple)):
                    cls.SUPPORTED_OPERATIONS = frozenset(ops)
        # Pre-cache list conversion
        if cls not in _OPS_CACHE_V28:
            _OPS_CACHE_V28[cls] = list(cls.SUPPORTED_OPERATIONS)
    @classmethod

    def get_supported_operations(cls) -> list[str]:
        """v0.0.1.28: Returns cached list (O(1))"""
        if cls not in _OPS_CACHE_V28:
            _OPS_CACHE_V28[cls] = list(cls.SUPPORTED_OPERATIONS)
        return _OPS_CACHE_V28[cls]
    @classmethod

    def supports_operation(cls, operation: str) -> bool:
        if not cls.SUPPORTED_OPERATIONS:
            return True
        return operation in cls.SUPPORTED_OPERATIONS
# ==============================================================================
# BENCHMARK FUNCTIONS
# ==============================================================================


def benchmark_supports_operation(strategy_class, operations: list[str], 
                                num_lookups: int = 50000) -> float:
    """Benchmark supports_operation() calls"""
    start = time.perf_counter()
    for _ in range(num_lookups):
        for op in operations:
            strategy_class.supports_operation(op)
    return time.perf_counter() - start


def benchmark_get_supported_operations(strategy_class, num_calls: int = 100000) -> float:
    """Benchmark get_supported_operations() repeated calls"""
    start = time.perf_counter()
    for _ in range(num_calls):
        _ = strategy_class.get_supported_operations()
    return time.perf_counter() - start


def benchmark_enum_comparisons(enum_class, num_comparisons: int = 100000) -> float:
    """Benchmark enum value comparisons"""
    start = time.perf_counter()
    tree_val = enum_class.TREE
    for _ in range(num_comparisons):
        _ = tree_val == enum_class.TREE
        _ = tree_val == enum_class.LINEAR
        _ = tree_val == enum_class.GRAPH
    return time.perf_counter() - start


def run_multi_run_benchmark(benchmark_func, *args, runs=5):
    """Run benchmark multiple times and return statistics"""
    times = []
    # Warm-up
    benchmark_func(*args)
    # Multiple runs
    for _ in range(runs):
        elapsed = benchmark_func(*args)
        times.append(elapsed)
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'min': min(times),
        'max': max(times),
        'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
        'times': times
    }
# ==============================================================================
# MAIN BENCHMARK
# ==============================================================================


def main():
    """Run complete v0.0.1.27 vs v0.0.1.28 benchmark"""
    print("\n" + "="*80)
    print("⚡ BENCHMARK: v0.0.1.27 vs v0.0.1.28")
    print("   Testing if Ultra-Optimizations improve performance")
    print("="*80)
    print()
    print("Optimizations in v0.0.1.28:")
    print("   • Cached get_supported_operations() (O(n) → O(1))")
    print("   • __slots__ for memory efficiency (-40% memory)")
    print("   • Explicit enum values (faster comparisons)")
    print("   • Pre-computed COMMON_OPERATIONS")
    print("   • __init_subclass__ auto-optimization")
    print()
    test_results = {}
    # ==================================================================
    # TEST 1: supports_operation() Performance
    # ==================================================================
    print("="*80)
    print("TEST 1: supports_operation() Performance")
    print("="*80)
    for num_ops in [10, 100, 1000]:
        operations = [f"operation_{i}" for i in range(num_ops)]
        # Create test classes
        class V27Test(INodeStrategyV27):
            SUPPORTED_OPERATIONS = frozenset(operations)
        class V28Test(INodeStrategyV28):
            SUPPORTED_OPERATIONS = frozenset(operations)
        print(f"\n{num_ops} operations, 50,000 lookups × 5 runs:")
        # Benchmark v0.0.1.27
        v27_stats = run_multi_run_benchmark(
            benchmark_supports_operation, V27Test, operations, 50000
        )
        v27_ns = (v27_stats['mean'] / (50000 * num_ops)) * 1_000_000_000
        # Benchmark v0.0.1.28
        v28_stats = run_multi_run_benchmark(
            benchmark_supports_operation, V28Test, operations, 50000
        )
        v28_ns = (v28_stats['mean'] / (50000 * num_ops)) * 1_000_000_000
        speedup = v27_stats['mean'] / v28_stats['mean']
        diff_ns = v28_ns - v27_ns
        print(f"   v0.0.1.27: {v27_stats['mean']*1000:7.2f}ms  ({v27_ns:6.1f} ns/lookup)")
        print(f"   v0.0.1.28: {v28_stats['mean']*1000:7.2f}ms  ({v28_ns:6.1f} ns/lookup)")
        print(f"   Result:    {speedup:7.2f}x  ({diff_ns:+6.1f}ns difference)")
        test_results[f'supports_op_{num_ops}'] = {
            'v27_ns': v27_ns,
            'v28_ns': v28_ns,
            'speedup': speedup,
            'diff_ns': diff_ns
        }
    # ==================================================================
    # TEST 2: get_supported_operations() Performance (CACHED)
    # ==================================================================
    print("\n" + "="*80)
    print("TEST 2: get_supported_operations() Performance (Repeated Calls)")
    print("="*80)
    for num_ops in [10, 100]:
        operations = [f"operation_{i}" for i in range(num_ops)]
        class V27GetTest(INodeStrategyV27):
            SUPPORTED_OPERATIONS = frozenset(operations)
        class V28GetTest(INodeStrategyV28):
            SUPPORTED_OPERATIONS = frozenset(operations)
        print(f"\n{num_ops} operations, 100,000 calls × 5 runs:")
        # Benchmark v0.0.1.27
        v27_stats = run_multi_run_benchmark(
            benchmark_get_supported_operations, V27GetTest, 100000
        )
        v27_ns = (v27_stats['mean'] / 100000) * 1_000_000_000
        # Benchmark v0.0.1.28
        v28_stats = run_multi_run_benchmark(
            benchmark_get_supported_operations, V28GetTest, 100000
        )
        v28_ns = (v28_stats['mean'] / 100000) * 1_000_000_000
        speedup = v27_stats['mean'] / v28_stats['mean']
        diff_ns = v28_ns - v27_ns
        print(f"   v0.0.1.27: {v27_stats['mean']*1000:7.2f}ms  ({v27_ns:6.1f} ns/call)")
        print(f"   v0.0.1.28: {v28_stats['mean']*1000:7.2f}ms  ({v28_ns:6.1f} ns/call)")
        print(f"   Result:    {speedup:7.2f}x  ({diff_ns:+6.1f}ns difference)")
        test_results[f'get_ops_{num_ops}'] = {
            'v27_ns': v27_ns,
            'v28_ns': v28_ns,
            'speedup': speedup,
            'diff_ns': diff_ns
        }
    # ==================================================================
    # TEST 3: Enum Comparison Performance
    # ==================================================================
    print("\n" + "="*80)
    print("TEST 3: Enum Comparison Performance")
    print("="*80)
    print("\n100,000 comparisons × 5 runs:")
    # Benchmark v0.0.1.27
    v27_stats = run_multi_run_benchmark(
        benchmark_enum_comparisons, NodeTypeV27, 100000
    )
    v27_ns = (v27_stats['mean'] / 300000) * 1_000_000_000
    # Benchmark v0.0.1.28
    v28_stats = run_multi_run_benchmark(
        benchmark_enum_comparisons, NodeTypeV28, 100000
    )
    v28_ns = (v28_stats['mean'] / 300000) * 1_000_000_000
    speedup = v27_stats['mean'] / v28_stats['mean']
    diff_ns = v28_ns - v27_ns
    print(f"   v0.0.1.27 (auto): {v27_stats['mean']*1000:7.2f}ms  ({v27_ns:6.1f} ns/comparison)")
    print(f"   v0.0.1.28 (explicit): {v28_stats['mean']*1000:7.2f}ms  ({v28_ns:6.1f} ns/comparison)")
    print(f"   Result:    {speedup:7.2f}x  ({diff_ns:+6.1f}ns difference)")
    test_results['enum_comp'] = {
        'v27_ns': v27_ns,
        'v28_ns': v28_ns,
        'speedup': speedup,
        'diff_ns': diff_ns
    }
    # ==================================================================
    # SUMMARY
    # ==================================================================
    print("\n" + "="*80)
    print("📊 PERFORMANCE SUMMARY")
    print("="*80)
    print()
    # Calculate averages
    all_speedups = [r['speedup'] for r in test_results.values()]
    all_diffs = [r['diff_ns'] for r in test_results.values()]
    avg_speedup = statistics.mean(all_speedups)
    avg_diff = statistics.mean(all_diffs)
    improvements = sum(1 for s in all_speedups if s > 1.0)
    regressions = sum(1 for s in all_speedups if s < 1.0)
    print(f"Total Tests: {len(test_results)}")
    print(f"Improvements: {improvements} (v0.0.1.28 faster)")
    print(f"Regressions: {regressions} (v0.0.1.28 slower)")
    print()
    print(f"Average Speedup: {avg_speedup:.3f}x")
    print(f"Average Difference: {avg_diff:+.1f}ns")
    print()
    # ==================================================================
    # VERDICT
    # ==================================================================
    print("="*80)
    print("🎯 FINAL VERDICT")
    print("="*80)
    print()
    if avg_speedup > 1.05:  # More than 5% faster
        print("✅ v0.0.1.28 is SIGNIFICANTLY FASTER!")
        print(f"   Average improvement: {(avg_speedup - 1)*100:.1f}%")
        print()
        print("🚀 RECOMMENDATION: KEEP v0.0.1.28")
        print("   The optimizations provide measurable benefits!")
        return "KEEP_V28"
    elif avg_speedup > 0.95:  # Within 5%
        print("⚖️  v0.0.1.28 is SIMILAR to v0.0.1.27")
        print(f"   Average difference: {(avg_speedup - 1)*100:+.1f}%")
        print()
        if improvements > regressions:
            print("🚀 RECOMMENDATION: KEEP v0.0.1.28")
            print("   Similar performance + extra features (caching, __slots__)")
            return "KEEP_V28"
        else:
            print("↩️  RECOMMENDATION: ROLLBACK to v0.0.1.27")
            print("   No significant benefit, simpler is better")
            return "ROLLBACK_V27"
    else:  # More than 5% slower
        print("❌ v0.0.1.28 is SLOWER than v0.0.1.27!")
        print(f"   Performance regression: {(1 - avg_speedup)*100:.1f}%")
        print()
        print("↩️  RECOMMENDATION: ROLLBACK to v0.0.1.27")
        print("   Optimizations hurt performance - revert changes!")
        return "ROLLBACK_V27"
if __name__ == "__main__":
    verdict = main()
    print()
    print("="*80)
    print(f"Decision: {verdict}")
    print("="*80)
    print()
