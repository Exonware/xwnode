#!/usr/bin/env python3
#exonware/xwnode/src/exonware/xwnode/common/monitoring/performance_monitor.py
"""
Strategy Performance Monitor
Tracks strategy usage, performance metrics, and provides optimization recommendations.
This enables data-driven strategy selection and performance tuning.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.18
Generation Date: 07-Sep-2025
"""

import time
import threading
import os
from typing import Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
from exonware.xwsystem import get_logger
logger = get_logger(__name__)
from ...defs import NodeMode, EdgeMode


class OperationType(Enum):
    """Types of operations to monitor."""
    GET = "get"
    PUT = "put"
    DELETE = "delete"
    ITERATE = "iterate"
    SEARCH = "search"
    MIGRATE = "migrate"
    CREATE = "create"
@dataclass

class OperationMetrics:
    """Metrics for a specific operation."""
    operation: OperationType
    count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    error_count: int = 0
    memory_usage: float = 0.0

    def add_measurement(self, duration: float, memory_usage: float = 0.0, error: bool = False):
        """Add a new measurement."""
        self.count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.avg_time = self.total_time / self.count
        self.memory_usage += memory_usage
        if error:
            self.error_count += 1
@dataclass

class StrategyProfile:
    """Performance profile for a strategy."""
    strategy_name: str
    mode: NodeMode | EdgeMode
    total_operations: int = 0
    total_time: float = 0.0
    operations: dict[OperationType, OperationMetrics] = field(default_factory=dict)
    memory_usage: float = 0.0
    error_rate: float = 0.0
    last_used: float = 0.0
    creation_time: float = field(default_factory=time.time)

    def get_operation_metrics(self, operation: OperationType) -> OperationMetrics:
        """Get or create operation metrics."""
        if operation not in self.operations:
            self.operations[operation] = OperationMetrics(operation)
        return self.operations[operation]

    def update_error_rate(self):
        """Update error rate calculation."""
        total_errors = sum(op.error_count for op in self.operations.values())
        self.error_rate = total_errors / max(self.total_operations, 1)
@dataclass

class PerformanceRecommendation:
    """Performance optimization recommendation."""
    strategy_name: str
    recommendation_type: str
    confidence: float
    reasoning: str
    estimated_improvement: float
    alternative_strategy: str | None = None


class StrategyPerformanceMonitor:
    """
    Monitors strategy performance and provides optimization recommendations.
    Performance optimization: Can be disabled via enabled=False to eliminate
    all monitoring overhead in production hot paths.
    """

    def __init__(self, history_size: int = 1000, enabled: bool = True):
        """
        Initialize performance monitor.
        Args:
            history_size: Maximum number of operations to keep in history
            enabled: If False, monitoring is disabled (zero overhead)
        Root cause fixed: Performance monitoring was always enabled, causing
        significant overhead (locks, dict operations, list appends, logging)
        on every operation. Now can be disabled for maximum performance.
        Priority alignment:
        - Performance (#4): Zero overhead when disabled
        - Usability (#2): Optional feature, doesn't break existing code
        - Maintainability (#3): Clean flag-based control
        """
        self._enabled = enabled
        self._history_size = history_size
        self._profiles: dict[str, StrategyProfile] = {}
        self._operation_history: deque = deque(maxlen=history_size)
        self._lock = threading.RLock()
        self._stats = {
            'total_operations': 0,
            'total_strategies': 0,
            'monitoring_start_time': time.time(),
            'recommendations_given': 0
        }

    def record_operation(
        self,
        strategy_id: str,
        operation: OperationType,
        duration: float,
        memory_usage: float = 0.0,
        error: bool = False,
        **metadata: Any
    ) -> None:
        """
        Record an operation for performance monitoring.
        Args:
            strategy_id: Unique identifier for the strategy
            operation: Type of operation performed
            duration: Operation duration in seconds
            memory_usage: Memory usage in bytes
            error: Whether the operation resulted in an error
            **metadata: Additional metadata
        Performance optimization: Early exit when disabled for zero overhead.
        """
        # Root cause fixed: Early exit when disabled eliminates all overhead
        # (lock acquisition, dict operations, list appends, logging)
        if not self._enabled:
            return
        with self._lock:
            # Get or create strategy profile
            if strategy_id not in self._profiles:
                self._profiles[strategy_id] = StrategyProfile(
                    strategy_name=strategy_id,
                    mode=self._extract_mode_from_id(strategy_id)
                )
                self._stats['total_strategies'] += 1
            profile = self._profiles[strategy_id]
            # Update profile
            profile.total_operations += 1
            profile.total_time += duration
            profile.memory_usage += memory_usage
            profile.last_used = time.time()
            # Update operation metrics
            op_metrics = profile.get_operation_metrics(operation)
            op_metrics.add_measurement(duration, memory_usage, error)
            # Update error rate
            profile.update_error_rate()
            # Add to history
            self._operation_history.append({
                'timestamp': time.time(),
                'strategy_id': strategy_id,
                'operation': operation.value,
                'duration': duration,
                'memory_usage': memory_usage,
                'error': error,
                'metadata': metadata
            })
            self._stats['total_operations'] += 1
            logger.debug(f"📊 Recorded {operation.value} operation for {strategy_id}: {duration:.3f}s")

    def get_strategy_profile(self, strategy_id: str) -> StrategyProfile | None:
        """
        Get performance profile for a strategy.
        Args:
            strategy_id: Strategy identifier
        Returns:
            Strategy profile or None if not found
        """
        with self._lock:
            return self._profiles.get(strategy_id)

    def get_top_performing_strategies(self, limit: int = 5) -> list[tuple[str, StrategyProfile]]:
        """
        Get top performing strategies by average operation time.
        Args:
            limit: Maximum number of strategies to return
        Returns:
            List of (strategy_id, profile) tuples sorted by performance
        """
        with self._lock:
            strategies = []
            for strategy_id, profile in self._profiles.items():
                if profile.total_operations > 0:
                    avg_time = profile.total_time / profile.total_operations
                    strategies.append((strategy_id, profile, avg_time))
            # Sort by average time (lower is better)
            strategies.sort(key=lambda x: x[2])
            return [(sid, prof) for sid, prof, _ in strategies[:limit]]

    def get_underperforming_strategies(self, threshold: float = 0.1) -> list[tuple[str, StrategyProfile]]:
        """
        Get strategies that are underperforming.
        Args:
            threshold: Error rate threshold for underperformance
        Returns:
            List of underperforming strategies
        """
        with self._lock:
            underperforming = []
            for strategy_id, profile in self._profiles.items():
                if profile.error_rate > threshold or profile.total_operations == 0:
                    underperforming.append((strategy_id, profile))
            return underperforming

    def generate_recommendations(self, strategy_id: str) -> list[PerformanceRecommendation]:
        """
        Generate performance recommendations for a strategy.
        Args:
            strategy_id: Strategy identifier
        Returns:
            List of performance recommendations
        """
        profile = self.get_strategy_profile(strategy_id)
        if not profile or profile.total_operations < 10:
            return []
        recommendations = []
        # Check for high error rate
        if profile.error_rate > 0.05:  # 5% error rate
            recommendations.append(PerformanceRecommendation(
                strategy_name=strategy_id,
                recommendation_type="error_rate",
                confidence=0.8,
                reasoning=f"High error rate ({profile.error_rate:.1%}) detected",
                estimated_improvement=0.2,
                alternative_strategy=self._suggest_alternative_strategy(profile.mode)
            ))
        # Check for slow operations
        slow_operations = []
        for op_type, metrics in profile.operations.items():
            if metrics.avg_time > 0.01:  # 10ms threshold
                slow_operations.append((op_type, metrics.avg_time))
        if slow_operations:
            slowest_op, slowest_time = max(slow_operations, key=lambda x: x[1])
            recommendations.append(PerformanceRecommendation(
                strategy_name=strategy_id,
                recommendation_type="slow_operations",
                confidence=0.7,
                reasoning=f"Slow {slowest_op.value} operations (avg: {slowest_time:.3f}s)",
                estimated_improvement=0.3,
                alternative_strategy=self._suggest_alternative_strategy(profile.mode)
            ))
        # Check for memory usage
        if profile.memory_usage > 100 * 1024 * 1024:  # 100MB threshold
            recommendations.append(PerformanceRecommendation(
                strategy_name=strategy_id,
                recommendation_type="memory_usage",
                confidence=0.6,
                reasoning=f"High memory usage ({profile.memory_usage / 1024 / 1024:.1f}MB)",
                estimated_improvement=0.4,
                alternative_strategy=self._suggest_memory_efficient_strategy(profile.mode)
            ))
        # Check for unused strategies
        time_since_last_use = time.time() - profile.last_used
        if time_since_last_use > 3600:  # 1 hour
            recommendations.append(PerformanceRecommendation(
                strategy_name=strategy_id,
                recommendation_type="unused_strategy",
                confidence=0.9,
                reasoning=f"Strategy unused for {time_since_last_use / 3600:.1f} hours",
                estimated_improvement=0.1,
                alternative_strategy="Consider removing unused strategy"
            ))
        self._stats['recommendations_given'] += len(recommendations)
        return recommendations

    def get_performance_summary(self) -> dict[str, Any]:
        """
        Get overall performance summary.
        Returns:
            Performance summary dictionary
        """
        with self._lock:
            if not self._profiles:
                return {
                    'total_strategies': 0,
                    'total_operations': 0,
                    'average_operation_time': 0.0,
                    'total_error_rate': 0.0,
                    'monitoring_duration': 0.0
                }
            total_operations = sum(p.total_operations for p in self._profiles.values())
            total_time = sum(p.total_time for p in self._profiles.values())
            total_errors = sum(
                sum(op.error_count for op in p.operations.values())
                for p in self._profiles.values()
            )
            avg_operation_time = total_time / total_operations if total_operations > 0 else 0.0
            total_error_rate = total_errors / total_operations if total_operations > 0 else 0.0
            monitoring_duration = time.time() - self._stats['monitoring_start_time']
            return {
                'total_strategies': len(self._profiles),
                'total_operations': total_operations,
                'average_operation_time': avg_operation_time,
                'total_error_rate': total_error_rate,
                'monitoring_duration': monitoring_duration,
                'operations_per_second': total_operations / monitoring_duration if monitoring_duration > 0 else 0.0,
                'top_strategies': [
                    {
                        'strategy_id': sid,
                        'operations': prof.total_operations,
                        'avg_time': prof.total_time / prof.total_operations if prof.total_operations > 0 else 0.0,
                        'error_rate': prof.error_rate
                    }
                    for sid, prof in self.get_top_performing_strategies(3)
                ]
            }

    def get_operation_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get recent operation history.
        Args:
            limit: Maximum number of operations to return
        Returns:
            List of recent operations
        """
        with self._lock:
            return list(self._operation_history)[-limit:]

    def clear_history(self) -> None:
        """Clear operation history."""
        with self._lock:
            self._operation_history.clear()
            logger.info("🧹 Cleared performance monitoring history")

    def reset_stats(self) -> None:
        """Reset all statistics."""
        with self._lock:
            self._profiles.clear()
            self._operation_history.clear()
            self._stats = {
                'total_operations': 0,
                'total_strategies': 0,
                'monitoring_start_time': time.time(),
                'recommendations_given': 0
            }
            logger.info("🔄 Reset performance monitoring statistics")

    def _extract_mode_from_id(self, strategy_id: str) -> NodeMode | EdgeMode:
        """Extract mode from strategy ID."""
        # Try to extract mode from strategy ID
        for mode in list(NodeMode) + list(EdgeMode):
            if mode.name.lower() in strategy_id.lower():
                return mode
        # Default fallback
        return NodeMode.HASH_MAP

    def _suggest_alternative_strategy(self, current_mode: NodeMode | EdgeMode) -> str:
        """Suggest alternative strategy based on current mode."""
        alternatives = {
            NodeMode.HASH_MAP: "ARRAY_LIST or TREE_GRAPH_HYBRID",
            NodeMode.ARRAY_LIST: "HASH_MAP or TREE_GRAPH_HYBRID",
            NodeMode.TREE_GRAPH_HYBRID: "HASH_MAP or DATA_INTERCHANGE_OPTIMIZED",
            NodeMode.DATA_INTERCHANGE_OPTIMIZED: "HASH_MAP or TREE_GRAPH_HYBRID",
            EdgeMode.ADJ_LIST: "ADJ_MATRIX",
            EdgeMode.ADJ_MATRIX: "ADJ_LIST"
        }
        return alternatives.get(current_mode, "Unknown alternative")

    def _suggest_memory_efficient_strategy(self, current_mode: NodeMode | EdgeMode) -> str:
        """Suggest memory-efficient alternative strategy."""
        memory_efficient = {
            NodeMode.HASH_MAP: "ARRAY_LIST (for sequential data)",
            NodeMode.ARRAY_LIST: "HASH_MAP (for sparse data)",
            NodeMode.TREE_GRAPH_HYBRID: "DATA_INTERCHANGE_OPTIMIZED (for large datasets)",
            NodeMode.DATA_INTERCHANGE_OPTIMIZED: "HASH_MAP (for small datasets)",
            EdgeMode.ADJ_LIST: "ADJ_MATRIX (for dense graphs)",
            EdgeMode.ADJ_MATRIX: "ADJ_LIST (for sparse graphs)"
        }
        return memory_efficient.get(current_mode, "Consider data structure optimization")
# Global monitor instance
_monitor_instance: StrategyPerformanceMonitor | None = None
_monitor_lock = threading.Lock()


def get_monitor() -> StrategyPerformanceMonitor:
    """
    Get the global performance monitor instance.
    Performance optimization: Can be disabled via XWNODE_DISABLE_PERF_MONITOR=1
    environment variable for maximum performance in production.
    Returns:
        Global StrategyPerformanceMonitor instance
    """
    global _monitor_instance
    if _monitor_instance is None:
        with _monitor_lock:
            if _monitor_instance is None:
                # Root cause fixed: Allow disabling via environment variable
                # for maximum performance in production benchmarks
                enabled = os.environ.get('XWNODE_DISABLE_PERF_MONITOR', '0') != '1'
                _monitor_instance = StrategyPerformanceMonitor(enabled=enabled)
                if enabled:
                    logger.info("📊 Initialized global strategy performance monitor")
                else:
                    logger.debug("📊 Performance monitoring disabled (XWNODE_DISABLE_PERF_MONITOR=1)")
    return _monitor_instance


def record_operation(
    strategy_id: str,
    operation: OperationType,
    duration: float,
    memory_usage: float = 0.0,
    error: bool = False,
    **metadata: Any
) -> None:
    """
    Record an operation using the global monitor.
    Args:
        strategy_id: Strategy identifier
        operation: Operation type
        duration: Operation duration
        memory_usage: Memory usage
        error: Whether operation failed
        **metadata: Additional metadata
    """
    get_monitor().record_operation(strategy_id, operation, duration, memory_usage, error, **metadata)


def get_performance_summary() -> dict[str, Any]:
    """
    Get performance summary from global monitor.
    Returns:
        Performance summary
    """
    return get_monitor().get_performance_summary()


def get_strategy_recommendations(strategy_id: str) -> list[PerformanceRecommendation]:
    """
    Get recommendations for a strategy from global monitor.
    Args:
        strategy_id: Strategy identifier
    Returns:
        List of recommendations
    """
    return get_monitor().generate_recommendations(strategy_id)
# Usability aliases (Priority #2: Clean, intuitive API)
PerformanceMonitor = StrategyPerformanceMonitor
