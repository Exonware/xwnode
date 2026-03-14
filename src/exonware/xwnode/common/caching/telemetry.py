"""
#exonware/xwnode/src/exonware/xwnode/common/caching/telemetry.py
Cache performance telemetry and proof-of-superiority tracking.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.7
Generation Date: November 4, 2025
"""

import time
import threading
from typing import Any
from dataclasses import dataclass, field
from collections import defaultdict
from exonware.xwsystem import get_logger
logger = get_logger(__name__)
@dataclass

class CachePerformanceMetric:
    """Performance metrics for cache operations."""
    operation: str
    cached: bool
    duration_ms: float
    timestamp: float
    component: str
    cache_strategy: str = "none"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'operation': self.operation,
            'cached': self.cached,
            'duration_ms': self.duration_ms,
            'timestamp': self.timestamp,
            'component': self.component,
            'cache_strategy': self.cache_strategy
        }
@dataclass

class CacheComparisonReport:
    """Comparison report between baseline (no cache) and cached performance."""
    component: str
    operation: str
    baseline_avg_ms: float
    cached_avg_ms: float
    speedup_factor: float
    cache_hit_rate: float
    total_operations: int
    cached_operations: int
    baseline_operations: int
    memory_overhead_mb: float = 0.0
    @property

    def performance_improvement_pct(self) -> float:
        """Calculate performance improvement percentage."""
        if self.baseline_avg_ms == 0:
            return 0.0
        return ((self.baseline_avg_ms - self.cached_avg_ms) / self.baseline_avg_ms) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'component': self.component,
            'operation': self.operation,
            'baseline_avg_ms': round(self.baseline_avg_ms, 3),
            'cached_avg_ms': round(self.cached_avg_ms, 3),
            'speedup_factor': round(self.speedup_factor, 2),
            'performance_improvement_pct': round(self.performance_improvement_pct, 2),
            'cache_hit_rate': round(self.cache_hit_rate, 3),
            'total_operations': self.total_operations,
            'cached_operations': self.cached_operations,
            'baseline_operations': self.baseline_operations,
            'memory_overhead_mb': round(self.memory_overhead_mb, 3)
        }


class CacheTelemetryCollector:
    """
    Collects and analyzes cache performance telemetry.
    Provides proof-of-superiority by comparing baseline (no cache)
    vs cached performance across operations.
    """

    def __init__(self, max_samples: int = 10000):
        """
        Initialize telemetry collector.
        Args:
            max_samples: Maximum number of samples to keep in memory
        """
        self._lock = threading.RLock()
        self._max_samples = max_samples
        # Store raw metrics
        self._metrics: list[CachePerformanceMetric] = []
        # Aggregated statistics
        self._stats: dict[str, dict[str, Any]] = defaultdict(lambda: {
            'baseline': {'count': 0, 'total_ms': 0.0},
            'cached': {'count': 0, 'total_ms': 0.0}
        })
        # Cache hit tracking
        self._cache_hits: dict[str, int] = defaultdict(int)
        self._cache_misses: dict[str, int] = defaultdict(int)
        logger.info("CacheTelemetryCollector initialized")

    def record_operation(
        self,
        component: str,
        operation: str,
        duration_ms: float,
        cached: bool,
        cache_strategy: str = "none"
    ) -> None:
        """
        Record a cache operation performance metric.
        Args:
            component: Component name ('graph', 'traversal', etc.)
            operation: Operation name ('get_neighbors', 'traverse', etc.)
            duration_ms: Operation duration in milliseconds
            cached: Whether the operation was served from cache
            cache_strategy: Cache strategy used
        """
        with self._lock:
            # Create metric
            metric = CachePerformanceMetric(
                operation=operation,
                cached=cached,
                duration_ms=duration_ms,
                timestamp=time.time(),
                component=component,
                cache_strategy=cache_strategy
            )
            # Store metric
            self._metrics.append(metric)
            # Trim if needed
            if len(self._metrics) > self._max_samples:
                self._metrics = self._metrics[-self._max_samples:]
            # Update aggregated stats
            key = f"{component}:{operation}"
            if cached:
                self._stats[key]['cached']['count'] += 1
                self._stats[key]['cached']['total_ms'] += duration_ms
                self._cache_hits[key] += 1
            else:
                self._stats[key]['baseline']['count'] += 1
                self._stats[key]['baseline']['total_ms'] += duration_ms
                self._cache_misses[key] += 1

    def get_comparison_report(
        self,
        component: str | None = None,
        operation: str | None = None
    ) -> list[CacheComparisonReport]:
        """
        Get performance comparison report.
        Args:
            component: Optional component filter
            operation: Optional operation filter
        Returns:
            List of comparison reports
        """
        with self._lock:
            reports = []
            for key, stats in self._stats.items():
                comp, op = key.split(':', 1)
                # Apply filters
                if component and comp != component:
                    continue
                if operation and op != operation:
                    continue
                # Calculate metrics
                baseline_count = stats['baseline']['count']
                cached_count = stats['cached']['count']
                if baseline_count == 0 and cached_count == 0:
                    continue
                baseline_avg = (stats['baseline']['total_ms'] / baseline_count
                               if baseline_count > 0 else 0.0)
                cached_avg = (stats['cached']['total_ms'] / cached_count
                            if cached_count > 0 else 0.0)
                # Calculate speedup
                if cached_avg > 0 and baseline_avg > 0:
                    speedup = baseline_avg / cached_avg
                else:
                    speedup = 1.0
                # Calculate hit rate
                total_requests = self._cache_hits[key] + self._cache_misses[key]
                hit_rate = (self._cache_hits[key] / total_requests
                          if total_requests > 0 else 0.0)
                report = CacheComparisonReport(
                    component=comp,
                    operation=op,
                    baseline_avg_ms=baseline_avg,
                    cached_avg_ms=cached_avg,
                    speedup_factor=speedup,
                    cache_hit_rate=hit_rate,
                    total_operations=baseline_count + cached_count,
                    cached_operations=cached_count,
                    baseline_operations=baseline_count
                )
                reports.append(report)
            # Sort by speedup factor (highest first)
            reports.sort(key=lambda r: r.speedup_factor, reverse=True)
            return reports

    def get_proof_summary(self) -> dict[str, Any]:
        """
        Get proof-of-superiority summary.
        Returns:
            Dictionary with proof metrics and summary
        """
        with self._lock:
            reports = self.get_comparison_report()
            if not reports:
                return {
                    'status': 'no_data',
                    'message': 'No performance data collected yet'
                }
            # Calculate overall metrics
            total_speedup = sum(r.speedup_factor for r in reports)
            avg_speedup = total_speedup / len(reports)
            avg_hit_rate = sum(r.cache_hit_rate for r in reports) / len(reports)
            avg_improvement_pct = sum(r.performance_improvement_pct for r in reports) / len(reports)
            # Find best and worst performers
            best = max(reports, key=lambda r: r.speedup_factor)
            worst = min(reports, key=lambda r: r.speedup_factor)
            # Count operations with significant speedup (>2x)
            significant_speedups = sum(1 for r in reports if r.speedup_factor > 2.0)
            return {
                'status': 'success',
                'overall_metrics': {
                    'avg_speedup_factor': round(avg_speedup, 2),
                    'avg_hit_rate': round(avg_hit_rate, 3),
                    'avg_improvement_pct': round(avg_improvement_pct, 2),
                    'operations_analyzed': len(reports),
                    'significant_speedups': significant_speedups,
                    'significant_speedup_pct': round((significant_speedups / len(reports)) * 100, 1)
                },
                'best_performer': {
                    'component': best.component,
                    'operation': best.operation,
                    'speedup_factor': round(best.speedup_factor, 2),
                    'improvement_pct': round(best.performance_improvement_pct, 2)
                },
                'worst_performer': {
                    'component': worst.component,
                    'operation': worst.operation,
                    'speedup_factor': round(worst.speedup_factor, 2),
                    'improvement_pct': round(worst.performance_improvement_pct, 2)
                },
                'recommendations': self._generate_recommendations(reports)
            }

    def _generate_recommendations(self, reports: list[CacheComparisonReport]) -> list[str]:
        """Generate recommendations based on reports."""
        recommendations = []
        for report in reports:
            if report.cache_hit_rate < 0.5:
                recommendations.append(
                    f"{report.component}.{report.operation}: Low hit rate ({report.cache_hit_rate:.1%}), "
                    f"consider increasing cache size or adjusting strategy"
                )
            if report.speedup_factor < 1.5 and report.cached_operations > 10:
                recommendations.append(
                    f"{report.component}.{report.operation}: Minimal speedup ({report.speedup_factor:.1f}x), "
                    f"consider disabling cache for this operation"
                )
            if report.speedup_factor > 10:
                recommendations.append(
                    f"{report.component}.{report.operation}: Excellent speedup ({report.speedup_factor:.1f}x), "
                    f"keep cache enabled"
                )
        return recommendations[:10]  # Limit to top 10

    def print_report(self, component: str | None = None) -> None:
        """
        Print formatted performance report.
        Args:
            component: Optional component filter
        """
        print("\n" + "="*80)
        print("CACHE PERFORMANCE REPORT (Proof of Superiority)")
        print("="*80)
        proof = self.get_proof_summary()
        if proof['status'] == 'no_data':
            print("\n⚠️  No performance data available yet")
            return
        metrics = proof['overall_metrics']
        print(f"\n📊 Overall Metrics:")
        print(f"  • Average Speedup:     {metrics['avg_speedup_factor']}x")
        print(f"  • Average Improvement: {metrics['avg_improvement_pct']:.1f}%")
        print(f"  • Average Hit Rate:    {metrics['avg_hit_rate']:.1%}")
        print(f"  • Operations Analyzed: {metrics['operations_analyzed']}")
        print(f"  • Significant Speedups: {metrics['significant_speedups']} "
              f"({metrics['significant_speedup_pct']:.1f}%)")
        best = proof['best_performer']
        print(f"\n🏆 Best Performer:")
        print(f"  • {best['component']}.{best['operation']}")
        print(f"  • Speedup: {best['speedup_factor']}x ({best['improvement_pct']:.1f}% faster)")
        worst = proof['worst_performer']
        print(f"\n⚠️  Worst Performer:")
        print(f"  • {worst['component']}.{worst['operation']}")
        print(f"  • Speedup: {worst['speedup_factor']}x ({worst['improvement_pct']:.1f}% faster)")
        if proof['recommendations']:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(proof['recommendations'], 1):
                print(f"  {i}. {rec}")
        print("\n" + "="*80 + "\n")
# Global telemetry collector instance
_telemetry_collector: CacheTelemetryCollector | None = None
_telemetry_lock = threading.Lock()


def get_telemetry_collector() -> CacheTelemetryCollector:
    """Get global telemetry collector instance."""
    global _telemetry_collector
    if _telemetry_collector is not None:
        return _telemetry_collector
    with _telemetry_lock:
        if _telemetry_collector is None:
            _telemetry_collector = CacheTelemetryCollector()
        return _telemetry_collector


def reset_telemetry() -> None:
    """Reset global telemetry collector."""
    global _telemetry_collector
    with _telemetry_lock:
        _telemetry_collector = None
        logger.info("Telemetry collector reset")
