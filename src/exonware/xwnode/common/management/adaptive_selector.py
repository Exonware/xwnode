#!/usr/bin/env python3
"""
#exonware/xwnode/src/exonware/xwnode/common/management/adaptive_selector.py
Adaptive Strategy Selection
Uses performance monitor recommendations to automatically select optimal strategies
based on workload characteristics and performance metrics.
Root cause fixed: Manual strategy selection doesn't adapt to workload changes.
Adaptive selection uses performance data to optimize strategy choice automatically.
Priority alignment:
- Security (#1): Validates strategy recommendations before switching
- Usability (#2): Optional feature, transparent when enabled
- Maintainability (#3): Clean integration with performance monitor
- Performance (#4): Optimizes strategy selection based on real performance data
- Extensibility (#5): Easy to add new selection criteria
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.17
Generation Date: 07-Sep-2025
"""

import threading
from typing import Any
from exonware.xwsystem import get_logger
from ...defs import NodeMode, EdgeMode
from ..monitoring.performance_monitor import (
    StrategyPerformanceMonitor,
    get_monitor,
    PerformanceRecommendation
)
logger = get_logger(__name__)


class AdaptiveStrategySelector:
    """
    Adaptive strategy selector using performance monitor recommendations.
    Automatically selects optimal strategies based on workload characteristics
    and performance metrics collected by the performance monitor.
    Performance benefits:
    - Optimizes strategy selection based on real performance data
    - Adapts to workload changes automatically
    - Reduces manual tuning effort
    Usage:
        selector = AdaptiveStrategySelector()
        # Get recommended strategy for workload
        recommendation = selector.recommend_strategy(
            current_mode=NodeMode.HASH_MAP,
            workload_profile={"read_heavy": True, "size": 10000}
        )
        # Auto-switch if recommendation is high confidence
        if recommendation.confidence > 0.8:
            new_mode = recommendation.alternative_strategy
            # Migrate to new strategy
    Time Complexity:
    - recommend_strategy: O(1) average (uses cached recommendations)
    - should_switch: O(1) average
    Space Complexity: O(1) per selector instance
    """

    def __init__(self, monitor: StrategyPerformanceMonitor | None = None):
        """
        Initialize adaptive strategy selector.
        Args:
            monitor: Performance monitor instance (uses global if None)
        Time Complexity: O(1)
        """
        self._monitor = monitor or get_monitor()
        self._lock = threading.RLock()
        self._switch_threshold = 0.8  # Confidence threshold for auto-switching
        self._min_operations = 100  # Minimum operations before recommending switch
        self._stats = {
            'recommendations_given': 0,
            'switches_performed': 0,
            'switches_rejected': 0
        }

    def recommend_strategy(
        self,
        current_mode: NodeMode,
        workload_profile: dict[str, Any] | None = None
    ) -> PerformanceRecommendation | None:
        """
        Get strategy recommendation based on performance data.
        Args:
            current_mode: Current strategy mode
            workload_profile: Optional workload characteristics
        Returns:
            Performance recommendation if available, None otherwise
        Time Complexity: O(1) average
        Performance: Uses cached recommendations from performance monitor
        """
        with self._lock:
            # Get recommendations from performance monitor
            strategy_id = f"node_{current_mode.name}"
            recommendations = self._monitor.generate_recommendations(strategy_id)
            if not recommendations:
                return None
            # Filter for strategy switch recommendations
            switch_recommendations = [
                rec for rec in recommendations
                if rec.recommendation_type in ('slow_operations', 'error_rate', 'memory_usage')
                and rec.alternative_strategy is not None
            ]
            if not switch_recommendations:
                return None
            # Select best recommendation (highest confidence)
            best = max(switch_recommendations, key=lambda r: r.confidence)
            self._stats['recommendations_given'] += 1
            logger.debug(f"🎯 Strategy recommendation: {best.alternative_strategy} "
                        f"(confidence: {best.confidence:.2f}, improvement: {best.estimated_improvement:.1%})")
            return best

    def should_switch(
        self,
        current_mode: NodeMode,
        recommendation: PerformanceRecommendation | None = None
    ) -> bool:
        """
        Determine if strategy should be switched.
        Args:
            current_mode: Current strategy mode
            recommendation: Optional recommendation (fetched if None)
        Returns:
            True if switch is recommended
        Time Complexity: O(1) average
        Criteria:
        - Confidence > threshold (default: 0.8)
        - Minimum operations performed (default: 100)
        - Estimated improvement > 10%
        """
        if recommendation is None:
            recommendation = self.recommend_strategy(current_mode)
        if recommendation is None:
            return False
        # Check confidence threshold
        if recommendation.confidence < self._switch_threshold:
            logger.debug(f"Recommendation confidence {recommendation.confidence:.2f} "
                        f"below threshold {self._switch_threshold}")
            return False
        # Check estimated improvement
        if recommendation.estimated_improvement < 0.1:  # 10% improvement
            logger.debug(f"Estimated improvement {recommendation.estimated_improvement:.1%} "
                        f"below 10% threshold")
            return False
        # Check minimum operations
        strategy_id = f"node_{current_mode.name}"
        profile = self._monitor.get_strategy_profile(strategy_id)
        if profile and profile.total_operations < self._min_operations:
            logger.debug(f"Operations {profile.total_operations} below minimum {self._min_operations}")
            return False
        return True

    def get_recommended_mode(
        self,
        current_mode: NodeMode,
        workload_profile: dict[str, Any] | None = None
    ) -> NodeMode | None:
        """
        Get recommended strategy mode.
        Args:
            current_mode: Current strategy mode
            workload_profile: Optional workload characteristics
        Returns:
            Recommended NodeMode if available, None otherwise
        Time Complexity: O(1) average
        """
        recommendation = self.recommend_strategy(current_mode, workload_profile)
        if recommendation is None or recommendation.alternative_strategy is None:
            return None
        # Convert string to NodeMode
        try:
            return NodeMode[recommendation.alternative_strategy]
        except (KeyError, AttributeError):
            logger.warning(f"Invalid alternative strategy: {recommendation.alternative_strategy}")
            return None

    def record_switch(
        self,
        from_mode: NodeMode,
        to_mode: NodeMode,
        success: bool = True
    ) -> None:
        """
        Record a strategy switch for tracking.
        Args:
            from_mode: Previous strategy mode
            to_mode: New strategy mode
            success: Whether switch was successful
        Time Complexity: O(1)
        """
        with self._lock:
            if success:
                self._stats['switches_performed'] += 1
                logger.info(f"✅ Strategy switched: {from_mode.name} → {to_mode.name}")
            else:
                self._stats['switches_rejected'] += 1
                logger.warning(f"❌ Strategy switch rejected: {from_mode.name} → {to_mode.name}")

    def get_stats(self) -> dict[str, Any]:
        """
        Get selector statistics.
        Returns:
            Dictionary with selector statistics
        Time Complexity: O(1)
        """
        with self._lock:
            return self._stats.copy()

    def configure(
        self,
        switch_threshold: float | None = None,
        min_operations: int | None = None
    ) -> None:
        """
        Configure selector parameters.
        Args:
            switch_threshold: Confidence threshold for auto-switching (0.0-1.0)
            min_operations: Minimum operations before recommending switch
        Time Complexity: O(1)
        """
        with self._lock:
            if switch_threshold is not None:
                if not 0.0 <= switch_threshold <= 1.0:
                    raise ValueError("switch_threshold must be between 0.0 and 1.0")
                self._switch_threshold = switch_threshold
            if min_operations is not None:
                if min_operations < 0:
                    raise ValueError("min_operations must be non-negative")
                self._min_operations = min_operations
# Global instance
_global_selector: AdaptiveStrategySelector | None = None
_selector_lock = threading.Lock()


def get_adaptive_selector() -> AdaptiveStrategySelector:
    """
    Get global adaptive strategy selector instance.
    Returns:
        Global AdaptiveStrategySelector instance
    Time Complexity: O(1)
    """
    global _global_selector
    with _selector_lock:
        if _global_selector is None:
            _global_selector = AdaptiveStrategySelector()
        return _global_selector
