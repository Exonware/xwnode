#!/usr/bin/env python3
"""
Quick benchmark for MASSTREE and T_TREE to compare before/after OrderedDict changes.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import time
import statistics
import json
from pathlib import Path
from typing import Any
from exonware.xwnode import XWNode
from exonware.xwnode.defs import NodeMode


def benchmark_strategy(mode: NodeMode, name: str, iterations: int = 1000) -> dict[str, Any]:
    """Benchmark a single strategy."""
    print(f"\n{'='*80}")
    print(f"Benchmarking: {name} ({mode.name})")
    print(f"{'='*80}")
    try:
        node = XWNode(mode=mode)
        # Warmup
        for i in range(100):
            node.put(f'warmup_key_{i}', f'warmup_value_{i}')
        results = {
            'mode': mode.name,
            'name': name,
            'error': None,
        }
        # Benchmark PUT
        times = []
        node.clear()
        for i in range(iterations):
            start = time.perf_counter()
            node.put(f'put_key_{i}', f'put_value_{i}')
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            times.append(elapsed)
        results['put_performance'] = {
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0.0,
            'ops_per_sec': 1000.0 / statistics.mean(times) if statistics.mean(times) > 0 else 0.0
        }
        print(f"  Put: {results['put_performance']['mean_ms']:.6f} ms/op ({results['put_performance']['ops_per_sec']:.0f} ops/sec)")
        # Benchmark GET
        times = []
        for i in range(iterations):
            key = f'put_key_{i % iterations}'
            start = time.perf_counter()
            value = node.get_value(key)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        results['get_performance'] = {
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0.0,
            'ops_per_sec': 1000.0 / statistics.mean(times) if statistics.mean(times) > 0 else 0.0
        }
        print(f"  Get: {results['get_performance']['mean_ms']:.6f} ms/op ({results['get_performance']['ops_per_sec']:.0f} ops/sec)")
        # Benchmark DELETE
        times = []
        for i in range(iterations):
            key = f'delete_key_{i}'
            node.put(key, f'delete_value_{i}')
            start = time.perf_counter()
            node.delete(key)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        results['delete_performance'] = {
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0.0,
            'ops_per_sec': 1000.0 / statistics.mean(times) if statistics.mean(times) > 0 else 0.0
        }
        print(f"  Delete: {results['delete_performance']['mean_ms']:.6f} ms/op ({results['delete_performance']['ops_per_sec']:.0f} ops/sec)")
        # Benchmark SIZE
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            size = len(node)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        results['size_performance'] = {
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0.0,
            'ops_per_sec': 1000.0 / statistics.mean(times) if statistics.mean(times) > 0 else 0.0
        }
        print(f"  Size: {results['size_performance']['mean_ms']:.6f} ms/op ({results['size_performance']['ops_per_sec']:.0f} ops/sec)")
        return results
    except Exception as e:
        error_msg = f"Failed to benchmark {name}: {str(e)}"
        print(f"  [ERROR] {error_msg}")
        return {
            'mode': mode.name,
            'name': name,
            'error': error_msg
        }


def compare_results(baseline: dict[str, Any], current: dict[str, Any], strategy_name: str):
    """Compare baseline and current results."""
    print(f"\n{'='*80}")
    print(f"Comparison: {strategy_name}")
    print(f"{'='*80}")
    if baseline.get('error') or current.get('error'):
        print(f"  ERROR: Cannot compare - one or both results have errors")
        return
    operations = ['put_performance', 'get_performance', 'delete_performance', 'size_performance']
    for op in operations:
        if op not in baseline or op not in current:
            continue
        baseline_mean = baseline[op].get('mean_ms', 0)
        current_mean = current[op].get('mean_ms', 0)
        if baseline_mean > 0:
            improvement = ((baseline_mean - current_mean) / baseline_mean) * 100
            speedup = baseline_mean / current_mean if current_mean > 0 else 0
        else:
            improvement = 0
            speedup = 0
        op_name = op.replace('_performance', '').upper()
        print(f"\n  {op_name}:")
        print(f"    Baseline: {baseline_mean:.6f} ms/op ({baseline[op].get('ops_per_sec', 0):.0f} ops/sec)")
        print(f"    Current:  {current_mean:.6f} ms/op ({current[op].get('ops_per_sec', 0):.0f} ops/sec)")
        if speedup > 0:
            print(f"    Improvement: {improvement:+.2f}% ({speedup:.2f}x {'faster' if speedup > 1 else 'slower'})")


def main():
    """Main entry point."""
    benchmark_dir = Path(__file__).parent
    # Load baseline results
    baseline_file = benchmark_dir / 'node_strategies_baseline.json'
    if baseline_file.exists():
        with open(baseline_file, 'r', encoding='utf-8') as f:
            baseline_data = json.load(f)
        masstree_baseline = baseline_data.get('MASSTREE', {})
        t_tree_baseline = baseline_data.get('T_TREE', {})
    else:
        print(f"[WARNING] Baseline file not found: {baseline_file}")
        masstree_baseline = {}
        t_tree_baseline = {}
    # Run current benchmarks
    iterations = 1000
    print(f"\nRunning benchmarks with {iterations} iterations each...")
    masstree_current = benchmark_strategy(NodeMode.MASSTREE, "Masstree", iterations)
    t_tree_current = benchmark_strategy(NodeMode.T_TREE, "T Tree", iterations)
    # Compare results
    if masstree_baseline:
        compare_results(masstree_baseline, masstree_current, "MASSTREE")
    if t_tree_baseline:
        compare_results(t_tree_baseline, t_tree_current, "T_TREE")
    # Save current results
    output_file = benchmark_dir / 'masstree_ttree_current.json'
    output_data = {
        'MASSTREE': masstree_current,
        'T_TREE': t_tree_current,
        'metadata': {
            'iterations': iterations,
            'timestamp': time.time()
        }
    }
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Current results saved to: {output_file}")
if __name__ == '__main__':
    main()
