#!/usr/bin/env python3
"""
Visual ASCII Chart: Performance Comparison

Creates visual representation of benchmark results.
"""

import sys

# Handle Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Benchmark data from results
data = [
    {"ops": 5, "old": 81.2, "new": 63.0, "speedup": 1.29},
    {"ops": 10, "old": 95.1, "new": 62.7, "speedup": 1.52},
    {"ops": 50, "old": 203.1, "new": 63.1, "speedup": 3.22},
    {"ops": 100, "old": 374.8, "new": 64.4, "speedup": 5.82},
    {"ops": 500, "old": 1413.5, "new": 62.7, "speedup": 22.53},
    {"ops": 1000, "old": 2882.0, "new": 65.5, "speedup": 44.03},
]

def create_bar_chart():
    """Create ASCII bar chart comparing OLD vs NEW"""
    
    print("\n" + "="*80)
    print("📊 Per-Lookup Time Comparison (nanoseconds)")
    print("="*80)
    print()
    
    max_val = max(d["old"] for d in data)
    scale = 60 / max_val  # Scale to fit in 60 chars
    
    for d in data:
        ops = d["ops"]
        old_val = d["old"]
        new_val = d["new"]
        speedup = d["speedup"]
        
        old_bar = "█" * int(old_val * scale)
        new_bar = "█" * int(new_val * scale)
        
        print(f"{ops:>4} ops:")
        print(f"  OLD: {old_bar} {old_val:>8.1f}ns")
        print(f"  NEW: {new_bar} {new_val:>8.1f}ns  ({speedup:.2f}x faster)")
        print()


def create_speedup_chart():
    """Create speedup visualization"""
    
    print("\n" + "="*80)
    print("⚡ Speedup Factor Chart")
    print("="*80)
    print()
    
    max_speedup = max(d["speedup"] for d in data)
    scale = 60 / max_speedup
    
    for d in data:
        ops = d["ops"]
        speedup = d["speedup"]
        bar = "▓" * int(speedup * scale)
        
        print(f"{ops:>4} ops: {bar} {speedup:>6.2f}x")
    
    print()


def create_time_complexity_demo():
    """Demonstrate O(1) vs O(n) scaling"""
    
    print("\n" + "="*80)
    print("📈 Time Complexity Demonstration")
    print("="*80)
    print()
    
    print("OLD Implementation (List) - O(n) Linear Scaling:")
    print()
    max_old = data[-1]["old"]
    scale = 60 / max_old
    
    for d in data:
        ops = d["ops"]
        time = d["old"]
        bar = "▒" * int(time * scale)
        print(f"  {ops:>4} ops: {bar} {time:>8.1f}ns")
    
    print("\n  ↑ Notice: Time increases linearly with operation count")
    
    print("\n" + "-"*80)
    print()
    print("NEW Implementation (Frozenset) - O(1) Constant Time:")
    print()
    
    for d in data:
        ops = d["ops"]
        time = d["new"]
        bar = "▓" * 20  # Constant width showing O(1)
        print(f"  {ops:>4} ops: {bar} {time:>8.1f}ns")
    
    print("\n  ↑ Notice: Time remains constant regardless of operation count")
    print()


def print_key_metrics():
    """Print key performance metrics"""
    
    print("\n" + "="*80)
    print("🎯 KEY PERFORMANCE METRICS")
    print("="*80)
    print()
    
    avg_speedup = sum(d["speedup"] for d in data) / len(data)
    max_speedup = max(d["speedup"] for d in data)
    min_speedup = min(d["speedup"] for d in data)
    
    # Calculate average times
    avg_old = sum(d["old"] for d in data) / len(data)
    avg_new = sum(d["new"] for d in data) / len(data)
    
    print(f"  Average OLD time:  {avg_old:>8.1f} ns/lookup")
    print(f"  Average NEW time:  {avg_new:>8.1f} ns/lookup")
    print(f"  Average Speedup:   {avg_speedup:>8.2f}x")
    print()
    print(f"  Minimum Speedup:   {min_speedup:>8.2f}x  (5 operations)")
    print(f"  Maximum Speedup:   {max_speedup:>8.2f}x  (1000 operations)")
    print()
    
    # Real-world scenario
    print("  Real-World Scenario (100 ops checked 1M times):")
    ops_100 = next(d for d in data if d["ops"] == 100)
    old_100 = ops_100["old"] * 1_000_000 / 1_000_000_000  # Convert to seconds
    new_100 = ops_100["new"] * 1_000_000 / 1_000_000_000
    savings = old_100 - new_100
    
    print(f"    OLD: {old_100:>6.2f} seconds")
    print(f"    NEW: {new_100:>6.2f} seconds")
    print(f"    💰 Time Saved: {savings:>6.2f} seconds ({savings*100/old_100:.1f}% reduction)")
    print()


def main():
    """Generate all visualizations"""
    
    print("\n")
    print("="*80)
    print("🎨 PERFORMANCE VISUALIZATION")
    print("   contracts.py Optimization: List → Frozenset")
    print("="*80)
    
    create_bar_chart()
    create_speedup_chart()
    create_time_complexity_demo()
    print_key_metrics()
    
    print("="*80)
    print("✅ Visualization Complete!")
    print("="*80)
    print()


if __name__ == "__main__":
    main()

