#!/usr/bin/env python3
#exonware/xnode/examples/enhanced_strategy_demo.py
"""
Enhanced Strategy System Demo
Demonstrates the enhanced xnode strategy system with:
- Flyweight pattern for memory optimization
- Intelligent pattern detection for AUTO mode selection
- Performance monitoring and optimization recommendations
- Comprehensive metrics and statistics tracking
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Sep-2025
"""

import time
import random
from typing import Any
# Import enhanced strategy components
from exonware.xnode.strategies import (
    StrategyManager, get_flyweight_stats, collect_comprehensive_metrics,
    get_metrics_summary, analyze_data_patterns, recommend_strategy,
    NodeMode, EdgeMode, NodeTrait, EdgeTrait
)


def demonstrate_flyweight_optimization():
    """Demonstrate flyweight pattern memory optimization."""
    print("🏭 Flyweight Pattern Demonstration")
    print("=" * 50)
    # Create multiple strategy managers with same configuration
    managers = []
    for i in range(5):
        manager = StrategyManager(
            node_mode=NodeMode.HASH_MAP,
            node_traits=NodeTrait.INDEXED
        )
        managers.append(manager)
    # Get flyweight statistics
    stats = get_flyweight_stats()
    print(f"📊 Flyweight Statistics:")
    print(f"   Node strategies created: {stats['node_strategies']['created']}")
    print(f"   Node strategies reused: {stats['node_strategies']['reused']}")
    print(f"   Cache hit rate: {stats['cache_performance']['hit_rate_percent']}%")
    print(f"   Memory saved instances: {stats['cache_performance']['memory_saved_instances']}")
    print()


def demonstrate_pattern_detection():
    """Demonstrate intelligent pattern detection."""
    print("🔍 Pattern Detection Demonstration")
    print("=" * 50)
    # Test different data patterns
    test_cases = [
        {
            'name': 'Sequential Array Data',
            'data': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'context': {'access_pattern': 'sequential'}
        },
        {
            'name': 'String Key Dictionary',
            'data': {'user': 'alice', 'age': 30, 'city': 'new york'},
            'context': {'access_pattern': 'random'}
        },
        {
            'name': 'Hierarchical Data',
            'data': {
                'users': {
                    'alice': {'age': 30, 'city': 'ny'},
                    'bob': {'age': 25, 'city': 'la'}
                },
                'products': {
                    'laptop': {'price': 1000},
                    'phone': {'price': 500}
                }
            },
            'context': {'access_pattern': 'mixed'}
        },
        {
            'name': 'Large Dataset',
            'data': {f'key_{i}': f'value_{i}' for i in range(1000)},
            'context': {'access_pattern': 'read_heavy'}
        }
    ]
    for test_case in test_cases:
        print(f"📋 Testing: {test_case['name']}")
        # Analyze data patterns
        profile = analyze_data_patterns(test_case['data'], **test_case['context'])
        # Get strategy recommendation
        recommendation = recommend_strategy(profile, 'node')
        print(f"   Detected patterns: {[p.value for p in profile.patterns]}")
        print(f"   Recommended strategy: {recommendation.mode.name}")
        print(f"   Confidence: {recommendation.confidence:.2f}")
        print(f"   Reasoning: {recommendation.reasoning}")
        print(f"   Estimated performance gain: {recommendation.estimated_performance_gain:.1%}")
        print()


def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring and optimization."""
    print("📊 Performance Monitoring Demonstration")
    print("=" * 50)
    # Create strategy manager
    manager = StrategyManager(node_mode=NodeMode.AUTO)
    # Simulate various operations with timing
    operations = [
        ('get', 0.001),
        ('put', 0.002),
        ('delete', 0.0015),
        ('iterate', 0.005),
        ('search', 0.003)
    ]
    print("🎯 Simulating operations...")
    for operation, base_time in operations:
        # Simulate operation with some variance
        duration = base_time + random.uniform(-0.0005, 0.0005)
        memory_usage = random.uniform(100, 1000)
        # Record operation
        manager.record_operation(operation, duration, memory_usage)
        print(f"   Recorded {operation}: {duration:.4f}s, {memory_usage:.0f} bytes")
    # Get performance summary
    summary = manager.get_enhanced_performance_summary()
    print(f"\n📈 Performance Summary:")
    print(f"   Total operations: {summary['monitor_summary']['total_operations']}")
    print(f"   Average operation time: {summary['monitor_summary']['average_operation_time']:.4f}s")
    print(f"   Total error rate: {summary['monitor_summary']['total_error_rate']:.2%}")
    # Get optimization recommendations
    recommendations = manager.get_optimization_recommendations()
    if recommendations.get('node'):
        print(f"\n💡 Optimization Recommendations:")
        for rec in recommendations['node']:
            print(f"   - {rec['type']}: {rec['reasoning']}")
            print(f"     Confidence: {rec['confidence']:.2f}, Improvement: {rec['estimated_improvement']:.1%}")
    print()


def demonstrate_comprehensive_metrics():
    """Demonstrate comprehensive metrics collection."""
    print("📊 Comprehensive Metrics Demonstration")
    print("=" * 50)
    # Collect comprehensive metrics
    metrics = collect_comprehensive_metrics()
    print("🏥 System Health:")
    health = metrics['system_health']
    print(f"   Status: {health['status'].upper()}")
    print(f"   Score: {health['score']:.1f}/100")
    print(f"   Total strategies: {health['total_strategies']}")
    print(f"   High error strategies: {health['high_error_strategies']}")
    print(f"   Slow strategies: {health['slow_strategies']}")
    print(f"\n💾 Memory Usage:")
    flyweight_stats = metrics['flyweight_metrics']
    print(f"   Active node strategies: {flyweight_stats['node_strategies']['active']}")
    print(f"   Active edge strategies: {flyweight_stats['edge_strategies']['active']}")
    print(f"   Cache hit rate: {flyweight_stats['cache_performance']['hit_rate_percent']}%")
    print(f"\n⚡ Performance Metrics:")
    perf_stats = metrics['performance_metrics']
    print(f"   Total operations: {perf_stats['total_operations']}")
    print(f"   Average operation time: {perf_stats['average_operation_time']:.4f}s")
    print(f"   Operations per second: {perf_stats['operations_per_second']:.2f}")
    # Get formatted summary
    summary = get_metrics_summary()
    print(f"\n📋 Formatted Summary:")
    print(summary)
    print()


def demonstrate_auto_mode_selection():
    """Demonstrate enhanced AUTO mode selection."""
    print("🤖 Enhanced AUTO Mode Selection")
    print("=" * 50)
    # Test different data types with AUTO mode
    test_data = [
        ([1, 2, 3, 4, 5], "Sequential list"),
        ({'a': 1, 'b': 2, 'c': 3}, "Simple dictionary"),
        ({'users': {'alice': {'age': 30}}, 'products': {'laptop': {'price': 1000}}}, "Hierarchical data"),
        ({f'item_{i}': i for i in range(100)}, "Large dictionary")
    ]
    for data, description in test_data:
        print(f"📋 Testing: {description}")
        # Create manager with AUTO mode
        manager = StrategyManager(
            node_mode=NodeMode.AUTO,
            initial_data=data
        )
        # Get strategy info
        info = manager.get_strategy_info()
        current_mode = info['node']['current_mode']
        print(f"   Data type: {type(data).__name__}")
        print(f"   Selected strategy: {current_mode}")
        print(f"   Materialized: {info['node']['materialized']}")
        print()


def main():
    """Run all demonstrations."""
    print("🚀 Enhanced XWNode Strategy System Demo")
    print("=" * 60)
    print()
    try:
        # Run all demonstrations
        demonstrate_flyweight_optimization()
        demonstrate_pattern_detection()
        demonstrate_performance_monitoring()
        demonstrate_comprehensive_metrics()
        demonstrate_auto_mode_selection()
        print("✅ All demonstrations completed successfully!")
        print()
        print("🎉 Enhanced Strategy System Features:")
        print("   ✓ Flyweight pattern for memory optimization")
        print("   ✓ Intelligent pattern detection for AUTO mode")
        print("   ✓ Performance monitoring and recommendations")
        print("   ✓ Comprehensive metrics and statistics")
        print("   ✓ Enhanced strategy management")
        print("   ✓ 100% backward compatibility")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
if __name__ == "__main__":
    main()
