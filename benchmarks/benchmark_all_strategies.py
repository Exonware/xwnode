#!/usr/bin/env python3
"""
#exonware/xwnode/benchmarks/benchmark_all_strategies.py
Comprehensive Benchmark Suite for All XWNode Strategies
This script benchmarks all node and edge strategies to establish baseline
performance metrics before optimizations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
"""

import time
import statistics
from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import logging
# xwsystem is a required dependency - no try/catch needed
from exonware.xwsystem import get_logger
# xwnode dependencies - all required, no try/catch
from exonware.xwnode import XWNode
from exonware.xwnode.facades.graph import XWNodeGraph
from exonware.xwnode.defs import NodeMode, EdgeMode
# Setup logger (xwsystem get_logger handles UTF encoding safely)
logger = get_logger(__name__)


def get_strategy_params(mode: NodeMode) -> Dict[str, Any]:
    """
    Get strategy-specific parameters for initialization.
    Args:
        mode: NodeMode to get parameters for
    Returns:
        Dictionary of parameters for XWNode initialization
    """
    params = {}
    # Cache strategies that need max_size
    if mode in (NodeMode.LRU_CACHE,):
        params['max_size'] = 1000
    # Probabilistic structures that need parameters
    if mode == NodeMode.COUNT_MIN_SKETCH:
        params['epsilon'] = 0.01
        params['delta'] = 0.01
    elif mode == NodeMode.HYPERLOGLOG:
        params['precision'] = 14
    elif mode == NodeMode.BLOOM_FILTER:
        params['capacity'] = 10000
        params['error_rate'] = 0.01
    # Histogram that needs parameters
    elif mode == NodeMode.HISTOGRAM:
        params['num_buckets'] = 100
        params['histogram_type'] = 'equi-width'
    # TDigest that needs parameters
    elif mode == NodeMode.T_DIGEST:
        params['compression'] = 100
    return params


class StrategyBenchmark:
    """Benchmark a single strategy."""

    def __init__(self, mode: NodeMode, name: str, setup_func=None):
        """
        Initialize benchmark.
        Args:
            mode: NodeMode to benchmark
            name: Human-readable name
            setup_func: Optional function to setup test data
        """
        self.mode = mode
        self.name = name
        self.setup_func = setup_func
        self.results: Dict[str, Any] = {}

    def run_benchmark(self, iterations: int = 1000, warmup: int = 100) -> Dict[str, Any]:
        """
        Run comprehensive benchmark suite.
        Args:
            iterations: Number of iterations for each test
            warmup: Number of warmup iterations
        Returns:
            Dictionary with benchmark results
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Benchmarking: {self.name} ({self.mode.name})")
        logger.info(f"{'='*80}")
        try:
            # Get strategy-specific parameters
            params = get_strategy_params(self.mode)
            # Create strategy instance with parameters
            node = XWNode(mode=self.mode, **params)
            # Setup test data if provided
            test_data = None
            if self.setup_func:
                test_data = self.setup_func()
            # Warmup
            try:
                self._warmup(node, warmup, test_data)
            except Exception as e:
                logger.warning(f"  Warmup failed: {e}")
            # Run benchmarks
            results = {
                'mode': self.mode.name,
                'name': self.name,
                'error': None,
            }
            # Benchmark each operation with error handling
            try:
                results['put_performance'] = self._benchmark_put(node, iterations, test_data)
            except Exception as e:
                logger.warning(f"  Put benchmark failed: {e}")
                results['put_performance'] = {'error': str(e)}
            try:
                results['get_performance'] = self._benchmark_get(node, iterations, test_data)
            except Exception as e:
                logger.warning(f"  Get benchmark failed: {e}")
                results['get_performance'] = {'error': str(e)}
            try:
                results['delete_performance'] = self._benchmark_delete(node, iterations, test_data)
            except Exception as e:
                logger.warning(f"  Delete benchmark failed: {e}")
                results['delete_performance'] = {'error': str(e)}
            try:
                results['iteration_performance'] = self._benchmark_iteration(node, iterations, test_data)
            except Exception as e:
                logger.warning(f"  Iteration benchmark failed: {e}")
                results['iteration_performance'] = {'error': str(e)}
            try:
                results['size_performance'] = self._benchmark_size(node, iterations)
            except Exception as e:
                logger.warning(f"  Size benchmark failed: {e}")
                results['size_performance'] = {'error': str(e)}
            # Strategy-specific benchmarks
            if hasattr(node, '_strategy') and hasattr(node._strategy, 'clear'):
                try:
                    results['clear_performance'] = self._benchmark_clear(node, iterations, test_data)
                except Exception as e:
                    logger.warning(f"  Clear benchmark failed: {e}")
                    results['clear_performance'] = {'error': str(e)}
            self.results = results
            return results
        except Exception as e:
            error_msg = f"Failed to benchmark {self.name}: {str(e)}"
            logger.error(f"  [ERROR] {error_msg}")
            self.results = {
                'mode': self.mode.name,
                'name': self.name,
                'error': error_msg
            }
            return self.results

    def _warmup(self, node: XWNode, iterations: int, test_data: Optional[Dict] = None) -> None:
        """Warmup phase to stabilize performance."""
        # Check if strategy requires numeric indices (e.g., ARRAY_LIST)
        strategy_mode = node._strategy.mode if hasattr(node, '_strategy') and hasattr(node._strategy, 'mode') else None
        requires_numeric = strategy_mode == NodeMode.ARRAY_LIST
        if test_data:
            for key, value in test_data.items():
                if requires_numeric:
                    try:
                        numeric_key = int(key)
                        node.put(numeric_key, value)
                    except (ValueError, TypeError):
                        pass  # Skip non-numeric keys
                else:
                    node.put(str(key), value)
        else:
            for i in range(min(iterations, 100)):
                if requires_numeric:
                    node.put(i, f'value_{i}')
                else:
                    node.put(f'key_{i}', f'value_{i}')

    def _benchmark_put(self, node: XWNode, iterations: int, test_data: Optional[Dict] = None) -> Dict[str, float]:
        """Benchmark put operations."""
        times = []
        # Check if strategy requires numeric indices
        strategy_mode = node._strategy.mode if hasattr(node, '_strategy') and hasattr(node._strategy, 'mode') else None
        requires_numeric = strategy_mode == NodeMode.ARRAY_LIST
        # Clear before benchmark
        if hasattr(node, 'clear'):
            node.clear()
        for i in range(iterations):
            if requires_numeric:
                key = i
            else:
                key = f'put_key_{i}'
            value = f'put_value_{i}'
            start = time.perf_counter()
            node.put(key, value)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # Convert to ms
        return {
            'mean_ms': statistics.mean(times) if times else 0.0,
            'median_ms': statistics.median(times) if times else 0.0,
            'min_ms': min(times) if times else 0.0,
            'max_ms': max(times) if times else 0.0,
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0.0,
            'ops_per_sec': 1000.0 / statistics.mean(times) if times and statistics.mean(times) > 0 else 0.0
        }

    def _benchmark_get(self, node: XWNode, iterations: int, test_data: Optional[Dict] = None) -> Dict[str, float]:
        """Benchmark get operations."""
        # Check if strategy requires numeric indices
        strategy_mode = node._strategy.mode if hasattr(node, '_strategy') and hasattr(node._strategy, 'mode') else None
        requires_numeric = strategy_mode == NodeMode.ARRAY_LIST
        # Prepare data
        if test_data:
            for key, value in test_data.items():
                if requires_numeric:
                    try:
                        numeric_key = int(key)
                        node.put(numeric_key, value)
                    except (ValueError, TypeError):
                        pass
                else:
                    node.put(str(key), value)
        else:
            for i in range(iterations):
                if requires_numeric:
                    node.put(i, f'get_value_{i}')
                else:
                    node.put(f'get_key_{i}', f'get_value_{i}')
        times = []
        for i in range(iterations):
            if requires_numeric:
                key = i % iterations
            else:
                key = f'get_key_{i % iterations}'
            start = time.perf_counter()
            value = node.get_value(key)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # Convert to ms
        return {
            'mean_ms': statistics.mean(times) if times else 0.0,
            'median_ms': statistics.median(times) if times else 0.0,
            'min_ms': min(times) if times else 0.0,
            'max_ms': max(times) if times else 0.0,
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0.0,
            'ops_per_sec': 1000.0 / statistics.mean(times) if times and statistics.mean(times) > 0 else 0.0
        }

    def _benchmark_delete(self, node: XWNode, iterations: int, test_data: Optional[Dict] = None) -> Dict[str, float]:
        """Benchmark delete operations."""
        times = []
        # Check if strategy requires numeric indices
        strategy_mode = node._strategy.mode if hasattr(node, '_strategy') and hasattr(node._strategy, 'mode') else None
        requires_numeric = strategy_mode == NodeMode.ARRAY_LIST
        # Prepare data for each iteration
        for i in range(iterations):
            if requires_numeric:
                key = i
            else:
                key = f'delete_key_{i}'
            node.put(key, f'delete_value_{i}')
            start = time.perf_counter()
            node.delete(key)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # Convert to ms
        return {
            'mean_ms': statistics.mean(times) if times else 0.0,
            'median_ms': statistics.median(times) if times else 0.0,
            'min_ms': min(times) if times else 0.0,
            'max_ms': max(times) if times else 0.0,
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0.0,
            'ops_per_sec': 1000.0 / statistics.mean(times) if times and statistics.mean(times) > 0 else 0.0
        }

    def _benchmark_iteration(self, node: XWNode, iterations: int, test_data: Optional[Dict] = None) -> Dict[str, float]:
        """Benchmark iteration (keys/values/items)."""
        # Check if strategy requires numeric indices
        strategy_mode = node._strategy.mode if hasattr(node, '_strategy') and hasattr(node._strategy, 'mode') else None
        requires_numeric = strategy_mode == NodeMode.ARRAY_LIST
        # Prepare data
        if test_data:
            for key, value in test_data.items():
                if requires_numeric:
                    try:
                        numeric_key = int(key)
                        node.put(numeric_key, value)
                    except (ValueError, TypeError):
                        pass
                else:
                    node.put(str(key), value)
        else:
            for i in range(iterations):
                if requires_numeric:
                    node.put(i, f'iter_value_{i}')
                else:
                    node.put(f'iter_key_{i}', f'iter_value_{i}')
        times = []
        for _ in range(min(iterations // 10, 100)):  # Fewer iterations for expensive operations
            start = time.perf_counter()
            list(node.keys())
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # Convert to ms
        return {
            'mean_ms': statistics.mean(times) if times else 0.0,
            'median_ms': statistics.median(times) if times else 0.0,
            'min_ms': min(times) if times else 0.0,
            'max_ms': max(times) if times else 0.0,
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0.0,
        }

    def _benchmark_size(self, node: XWNode, iterations: int) -> Dict[str, float]:
        """Benchmark size/len operations."""
        # Check if strategy requires numeric indices
        strategy_mode = node._strategy.mode if hasattr(node, '_strategy') and hasattr(node._strategy, 'mode') else None
        requires_numeric = strategy_mode == NodeMode.ARRAY_LIST
        # Prepare data
        for i in range(iterations):
            if requires_numeric:
                node.put(i, f'size_value_{i}')
            else:
                node.put(f'size_key_{i}', f'size_value_{i}')
        times = []
        for _ in range(iterations * 10):  # Many iterations for very fast operations
            start = time.perf_counter()
            _ = len(node)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # Convert to ms
        return {
            'mean_ms': statistics.mean(times) if times else 0.0,
            'median_ms': statistics.median(times) if times else 0.0,
            'min_ms': min(times) if times else 0.0,
            'max_ms': max(times) if times else 0.0,
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0.0,
            'ops_per_sec': 1000.0 / statistics.mean(times) if times and statistics.mean(times) > 0 else 0.0
        }

    def _benchmark_clear(self, node: XWNode, iterations: int, test_data: Optional[Dict] = None) -> Dict[str, float]:
        """Benchmark clear operations."""
        times = []
        # Check if strategy requires numeric indices
        strategy_mode = node._strategy.mode if hasattr(node, '_strategy') and hasattr(node._strategy, 'mode') else None
        requires_numeric = strategy_mode == NodeMode.ARRAY_LIST
        for _ in range(min(iterations // 10, 100)):  # Fewer iterations
            # Prepare data
            if test_data:
                for key, value in test_data.items():
                    if requires_numeric:
                        try:
                            numeric_key = int(key)
                            node.put(numeric_key, value)
                        except (ValueError, TypeError):
                            pass
                    else:
                        node.put(str(key), value)
            else:
                for i in range(100):
                    if requires_numeric:
                        node.put(i, f'clear_value_{i}')
                    else:
                        node.put(f'clear_key_{i}', f'clear_value_{i}')
            start = time.perf_counter()
            node.clear()
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # Convert to ms
        return {
            'mean_ms': statistics.mean(times) if times else 0.0,
            'median_ms': statistics.median(times) if times else 0.0,
            'min_ms': min(times) if times else 0.0,
            'max_ms': max(times) if times else 0.0,
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0.0,
        }

    def print_results(self) -> None:
        """Print benchmark results in human-readable format."""
        if 'error' in self.results and self.results['error']:
            logger.error(f"  [ERROR] {self.results['error']}")
            return
        if 'put_performance' not in self.results:
            logger.warning(f"  [WARNING] {self.name}: Missing performance data")
            return
        # Print results with error handling
        try:
            put = self.results.get('put_performance', {})
            if 'error' not in put:
                logger.info(f"  Put (mean):      {put.get('mean_ms', 0):.4f} ms ({put.get('ops_per_sec', 0):.0f} ops/s)")
            else:
                logger.warning(f"  Put: ERROR - {put.get('error', 'Unknown')}")
        except Exception:
            logger.warning(f"  Put: Failed to print results")
        try:
            get = self.results.get('get_performance', {})
            if 'error' not in get:
                logger.info(f"  Get (mean):      {get.get('mean_ms', 0):.4f} ms ({get.get('ops_per_sec', 0):.0f} ops/s)")
            else:
                logger.warning(f"  Get: ERROR - {get.get('error', 'Unknown')}")
        except Exception:
            logger.warning(f"  Get: Failed to print results")
        try:
            delete = self.results.get('delete_performance', {})
            if 'error' not in delete:
                logger.info(f"  Delete (mean):   {delete.get('mean_ms', 0):.4f} ms ({delete.get('ops_per_sec', 0):.0f} ops/s)")
            else:
                logger.warning(f"  Delete: ERROR - {delete.get('error', 'Unknown')}")
        except Exception:
            logger.warning(f"  Delete: Failed to print results")
        try:
            size = self.results.get('size_performance', {})
            if 'error' not in size:
                logger.info(f"  Size (mean):     {size.get('mean_ms', 0):.4f} ms ({size.get('ops_per_sec', 0):.0f} ops/s)")
            else:
                logger.warning(f"  Size: ERROR - {size.get('error', 'Unknown')}")
        except Exception:
            logger.warning(f"  Size: Failed to print results")
        if 'clear_performance' in self.results:
            try:
                clear = self.results['clear_performance']
                if 'error' not in clear:
                    logger.info(f"  Clear (mean):    {clear.get('mean_ms', 0):.4f} ms")
                else:
                    logger.warning(f"  Clear: ERROR - {clear.get('error', 'Unknown')}")
            except Exception:
                logger.warning(f"  Clear: Failed to print results")


class EdgeStrategyBenchmark:
    """Benchmark a single edge strategy (using XWNodeGraph)."""

    def __init__(self, edge_mode: EdgeMode, name: str):
        """Initialize edge benchmark."""
        self.edge_mode = edge_mode
        self.name = name
        self.results: Dict[str, Any] = {}

    def run_benchmark(self, iterations: int = 100, warmup: int = 10) -> Dict[str, Any]:
        """Run benchmark for edge strategy."""
        logger.info(f"\n{'='*80}")
        logger.info(f"Benchmarking Edge: {self.name} ({self.edge_mode.name})")
        logger.info(f"{'='*80}")
        try:
            # Create graph with this edge mode
            graph = XWNodeGraph(
                node_mode=NodeMode.HASH_MAP,
                edge_mode=self.edge_mode
            )
            # Warmup
            try:
                for i in range(warmup):
                    graph.add_node(f'node_{i}', data=f'data_{i}')
                for i in range(warmup - 1):
                    graph.add_edge(f'node_{i}', f'node_{i+1}')
            except Exception as e:
                logger.warning(f"  Warmup failed: {e}")
            # Benchmark add_edge
            edge_times = []
            try:
                for i in range(iterations):
                    start = time.perf_counter()
                    graph.add_edge(f'edge_src_{i}', f'edge_tgt_{i}')
                    elapsed = time.perf_counter() - start
                    edge_times.append(elapsed * 1000)
            except Exception as e:
                logger.warning(f"  Add edge benchmark failed: {e}")
            # Benchmark get_neighbors (if supported)
            neighbor_times = []
            try:
                if hasattr(graph, 'get_neighbors'):
                    for i in range(min(iterations, 100)):
                        start = time.perf_counter()
                        try:
                            _ = graph.get_neighbors(f'node_{i % warmup}')
                        except:
                            pass
                        elapsed = time.perf_counter() - start
                        neighbor_times.append(elapsed * 1000)
            except Exception as e:
                logger.warning(f"  Get neighbors benchmark failed: {e}")
            results = {
                'mode': self.edge_mode.name,
                'name': self.name,
                'error': None,
                'add_edge_performance': {
                    'mean_ms': statistics.mean(edge_times) if edge_times else 0.0,
                    'median_ms': statistics.median(edge_times) if edge_times else 0.0,
                    'min_ms': min(edge_times) if edge_times else 0.0,
                    'max_ms': max(edge_times) if edge_times else 0.0,
                    'ops_per_sec': 1000.0 / statistics.mean(edge_times) if edge_times and statistics.mean(edge_times) > 0 else 0.0
                }
            }
            if neighbor_times:
                results['get_neighbors_performance'] = {
                    'mean_ms': statistics.mean(neighbor_times),
                    'median_ms': statistics.median(neighbor_times),
                    'min_ms': min(neighbor_times),
                    'max_ms': max(neighbor_times),
                }
            self.results = results
            return results
        except Exception as e:
            error_msg = f"Failed to benchmark {self.name}: {str(e)}"
            logger.error(f"  [ERROR] {error_msg}")
            self.results = {
                'mode': self.edge_mode.name,
                'name': self.name,
                'error': error_msg
            }
            return self.results

    def print_results(self) -> None:
        """Print edge benchmark results."""
        if 'error' in self.results and self.results['error']:
            logger.error(f"  [ERROR] {self.results['error']}")
            return
        try:
            add_edge = self.results.get('add_edge_performance', {})
            if 'error' not in add_edge:
                logger.info(f"  Add Edge (mean): {add_edge.get('mean_ms', 0):.4f} ms ({add_edge.get('ops_per_sec', 0):.0f} ops/s)")
            else:
                logger.warning(f"  Add Edge: ERROR - {add_edge.get('error', 'Unknown')}")
        except Exception:
            logger.warning(f"  Add Edge: Failed to print results")
        if 'get_neighbors_performance' in self.results:
            try:
                neighbors = self.results['get_neighbors_performance']
                if 'error' not in neighbors:
                    logger.info(f"  Get Neighbors (mean): {neighbors.get('mean_ms', 0):.4f} ms")
                else:
                    logger.warning(f"  Get Neighbors: ERROR - {neighbors.get('error', 'Unknown')}")
            except Exception:
                logger.warning(f"  Get Neighbors: Failed to print results")


def get_all_node_modes() -> List[NodeMode]:
    """Get all NodeMode values (excluding AUTO)."""
    return [mode for mode in NodeMode if mode != NodeMode.AUTO]


def get_all_edge_modes() -> List[EdgeMode]:
    """Get all EdgeMode values (excluding AUTO)."""
    return [mode for mode in EdgeMode if mode != EdgeMode.AUTO]


def run_all_node_benchmarks(iterations: int = 1000, warmup: int = 100, output_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Run benchmarks for all node strategies.
    Args:
        iterations: Number of iterations per test
        warmup: Number of warmup iterations
        output_file: Optional file to save JSON results
    Returns:
        Dictionary with all benchmark results
    """
    logger.info("="*80)
    logger.info("XWNode Node Strategy Benchmark Suite")
    logger.info("="*80)
    logger.info(f"Iterations per test: {iterations}")
    logger.info(f"Warmup iterations: {warmup}")
    logger.info("")
    all_results = {}
    node_modes = get_all_node_modes()
    total_modes = len(node_modes)
    successful = 0
    failed = 0
    logger.info(f"Total node strategies to benchmark: {total_modes}")
    logger.info("")
    for idx, mode in enumerate(node_modes, 1):
        logger.info(f"[{idx}/{total_modes}] Benchmarking {mode.name}...")
        try:
            benchmark = StrategyBenchmark(mode, mode.name.replace('_', ' ').title())
            results = benchmark.run_benchmark(iterations=iterations, warmup=warmup)
            benchmark.print_results()
            if 'error' in results and results['error']:
                failed += 1
            else:
                successful += 1
            all_results[mode.name] = results
        except Exception as e:
            logger.error(f"  [FATAL ERROR] Failed to benchmark {mode.name}: {e}")
            all_results[mode.name] = {
                'mode': mode.name,
                'name': mode.name.replace('_', ' ').title(),
                'error': f"Fatal error: {str(e)}"
            }
            failed += 1
    logger.info("")
    logger.info(f"Node benchmarks complete: {successful} successful, {failed} failed")
    # Save results to file
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        logger.info(f"\n[OK] Results saved to: {output_file}")
    return all_results


def run_all_edge_benchmarks(iterations: int = 100, warmup: int = 10, output_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Run benchmarks for all edge strategies.
    Args:
        iterations: Number of iterations per test
        warmup: Number of warmup iterations
        output_file: Optional file to save JSON results
    Returns:
        Dictionary with all benchmark results
    """
    logger.info("="*80)
    logger.info("XWNode Edge Strategy Benchmark Suite")
    logger.info("="*80)
    logger.info(f"Iterations per test: {iterations}")
    logger.info(f"Warmup iterations: {warmup}")
    logger.info("")
    all_results = {}
    edge_modes = get_all_edge_modes()
    total_modes = len(edge_modes)
    successful = 0
    failed = 0
    logger.info(f"Total edge strategies to benchmark: {total_modes}")
    logger.info("")
    for idx, mode in enumerate(edge_modes, 1):
        logger.info(f"[{idx}/{total_modes}] Benchmarking {mode.name}...")
        try:
            benchmark = EdgeStrategyBenchmark(mode, mode.name.replace('_', ' ').title())
            results = benchmark.run_benchmark(iterations=iterations, warmup=warmup)
            benchmark.print_results()
            if 'error' in results and results['error']:
                failed += 1
            else:
                successful += 1
            all_results[mode.name] = results
        except Exception as e:
            logger.error(f"  [FATAL ERROR] Failed to benchmark {mode.name}: {e}")
            all_results[mode.name] = {
                'mode': mode.name,
                'name': mode.name.replace('_', ' ').title(),
                'error': f"Fatal error: {str(e)}"
            }
            failed += 1
    logger.info("")
    logger.info(f"Edge benchmarks complete: {successful} successful, {failed} failed")
    # Save results to file
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        logger.info(f"\n[OK] Results saved to: {output_file}")
    return all_results


def run_all_benchmarks(iterations: int = 1000, warmup: int = 100, output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Run benchmarks for all node and edge strategies.
    Args:
        iterations: Number of iterations per test (nodes)
        warmup: Number of warmup iterations
        output_dir: Optional directory to save JSON results
    Returns:
        Dictionary with all benchmark results
    """
    if output_dir is None:
        output_dir = Path(__file__).parent  # Use benchmarks directory
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    # Run node benchmarks
    node_results = run_all_node_benchmarks(
        iterations=iterations,
        warmup=warmup,
        output_file=output_dir / 'node_strategies_baseline.json'
    )
    # Run edge benchmarks
    edge_results = run_all_edge_benchmarks(
        iterations=min(iterations // 10, 100),  # Fewer iterations for edges
        warmup=min(warmup, 10),
        output_file=output_dir / 'edge_strategies_baseline.json'
    )
    # Combine results
    all_results = {
        'nodes': node_results,
        'edges': edge_results,
        'metadata': {
            'iterations': iterations,
            'warmup': warmup,
            'timestamp': time.time()
        }
    }
    # Save combined results
    combined_file = output_dir / 'all_strategies_baseline.json'
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    logger.info(f"\n[OK] Combined results saved to: {combined_file}")
    return all_results


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Benchmark all XWNode strategies (nodes and edges)')
    parser.add_argument('--iterations', type=int, default=1000, help='Iterations per test (nodes)')
    parser.add_argument('--warmup', type=int, default=100, help='Warmup iterations')
    parser.add_argument('--output-dir', type=Path, default=None, help='Output directory for JSON files (default: xwnode/benchmarks)')
    parser.add_argument('--nodes-only', action='store_true', help='Benchmark only node strategies')
    parser.add_argument('--edges-only', action='store_true', help='Benchmark only edge strategies')
    args = parser.parse_args()
    # Default output directory is benchmarks folder
    if args.output_dir is None:
        args.output_dir = Path(__file__).parent
    if args.nodes_only:
        results = run_all_node_benchmarks(
            iterations=args.iterations,
            warmup=args.warmup,
            output_file=args.output_dir / 'node_strategies_baseline.json'
        )
        total = len([r for r in results.values() if 'error' not in r])
        failed = len([r for r in results.values() if 'error' in r])
    elif args.edges_only:
        results = run_all_edge_benchmarks(
            iterations=min(args.iterations // 10, 100),
            warmup=min(args.warmup, 10),
            output_file=args.output_dir / 'edge_strategies_baseline.json'
        )
        total = len([r for r in results.values() if 'error' not in r])
        failed = len([r for r in results.values() if 'error' in r])
    else:
        results = run_all_benchmarks(
            iterations=args.iterations,
            warmup=args.warmup,
            output_dir=args.output_dir
        )
        node_total = len([r for r in results['nodes'].values() if 'error' not in r])
        node_failed = len([r for r in results['nodes'].values() if 'error' in r])
        edge_total = len([r for r in results['edges'].values() if 'error' not in r])
        edge_failed = len([r for r in results['edges'].values() if 'error' in r])
        total = node_total + edge_total
        failed = node_failed + edge_failed
    logger.info("\n" + "="*80)
    logger.info("Benchmark Complete")
    logger.info("="*80)
    logger.info(f"Total strategies benchmarked: {total}")
    logger.info(f"Failed strategies: {failed}")
if __name__ == '__main__':
    main()
