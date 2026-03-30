#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/common/benchmarking.py
Performance Benchmarking Utilities
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.16
Generation Date: 15-Nov-2025
"""

import time
import statistics
from typing import Any
from dataclasses import dataclass
from exonware.xwsystem import get_logger
from collections.abc import Callable
logger = get_logger(__name__)
@dataclass

class BenchmarkResult:
    """Result of a single benchmark run."""
    operation: str
    strategy: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    median_time: float
    std_dev: float
    throughput: float  # operations per second


class StrategyBenchmark:
    """Benchmark utilities for node strategies."""
    @staticmethod

    def benchmark_operation(
        operation: Callable[[], Any],
        operation_name: str,
        strategy_name: str,
        iterations: int = 1000,
        warmup: int = 100
    ) -> BenchmarkResult:
        """
        Benchmark a single operation.
        Args:
            operation: Function to benchmark (takes no args, returns result)
            operation_name: Name of the operation
            strategy_name: Name of the strategy
            iterations: Number of iterations to run
            warmup: Number of warmup iterations
        Returns:
            BenchmarkResult with statistics
        """
        # Warmup
        for _ in range(warmup):
            try:
                operation()
            except Exception:
                pass
        # Actual benchmark
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                operation()
            except Exception as e:
                logger.warning(f"Operation {operation_name} failed: {e}")
            end = time.perf_counter()
            times.append(end - start)
        total_time = sum(times)
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        throughput = iterations / total_time if total_time > 0 else 0.0
        return BenchmarkResult(
            operation=operation_name,
            strategy=strategy_name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            std_dev=std_dev,
            throughput=throughput
        )
    @staticmethod

    def benchmark_strategy(
        strategy: Any,
        operations: dict[str, Callable[[], Any]],
        iterations: int = 1000
    ) -> list[BenchmarkResult]:
        """
        Benchmark multiple operations on a strategy.
        Args:
            strategy: Strategy instance to benchmark
            operations: Dict of operation_name -> operation_function
            iterations: Number of iterations per operation
        Returns:
            List of BenchmarkResult objects
        """
        strategy_name = getattr(strategy, '__class__', {}).__name__ if hasattr(strategy, '__class__') else 'Unknown'
        results = []
        for op_name, op_func in operations.items():
            result = StrategyBenchmark.benchmark_operation(
                op_func,
                op_name,
                strategy_name,
                iterations
            )
            results.append(result)
        return results
    @staticmethod

    def compare_strategies(
        strategies: dict[str, Any],
        operations: dict[str, Callable[[], Any]],
        iterations: int = 1000
    ) -> dict[str, list[BenchmarkResult]]:
        """
        Compare multiple strategies on the same operations.
        Args:
            strategies: Dict of strategy_name -> strategy_instance
            operations: Dict of operation_name -> operation_function
            iterations: Number of iterations per operation
        Returns:
            Dict mapping strategy_name -> list of BenchmarkResult objects
        """
        comparison = {}
        for strategy_name, strategy in strategies.items():
            # Create operation functions bound to this strategy
            bound_operations = {}
            for op_name, op_func in operations.items():
                # Wrap operation to use this strategy
                def make_op(op_name, op_func, strat):
                    def wrapped():
                        # This will be called with strategy context
                        return op_func(strat)
                    return wrapped
                bound_operations[op_name] = make_op(op_name, op_func, strategy)
            results = StrategyBenchmark.benchmark_strategy(
                strategy,
                bound_operations,
                iterations
            )
            comparison[strategy_name] = results
        return comparison


def benchmark_node_operation(
    node: Any,
    operation: str,
    *args,
    iterations: int = 1000,
    **kwargs
) -> BenchmarkResult:
    """
    Convenience function to benchmark a node operation.
    Args:
        node: XWNode instance
        operation: Operation name (e.g., 'get', 'set', 'delete')
        *args: Arguments for the operation
        iterations: Number of iterations
        **kwargs: Keyword arguments for the operation
    Returns:
        BenchmarkResult
    """
    strategy_name = getattr(node, '_strategy', {}).__class__.__name__ if hasattr(node, '_strategy') else 'Unknown'
    def op():
        method = getattr(node, operation, None)
        if method:
            return method(*args, **kwargs)
        raise AttributeError(f"Operation {operation} not found")
    return StrategyBenchmark.benchmark_operation(
        op,
        operation,
        strategy_name,
        iterations
    )
