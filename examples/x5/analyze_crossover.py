#!/usr/bin/env python3
"""
Analyze performance data to estimate when V1 and V2 become comparable.
Based on the provided test results.
"""

import numpy as np
# Data from test results
# Format: (num_ops, v1_time_ms, v2_time_ms, comparison_name)
data = {
    "Comparison 1: First Access": [
        (100, 2.16, 13.97),
        (1000, 17.83, 1.47),
        (2000, 33.03, 0.6676),
    ],
    "Comparison 2: Random ID Access": [
        (100, 2.01, 16.30),
        (1000, 16.97, 1.31),
        (2000, 40.50, 1.07),
    ],
    "Comparison 3: ID-Based Lookup": [
        (100, 2.14, 13.75),
        (1000, 16.12, 1.24),
        (2000, 44.48, 0.74071),
    ],
    "Comparison 4: Paging": [
        (100, 0.40771, 13.93),
        (1000, 0.35691, 1.57),
        (2000, 0.42070, 1.11),
    ],
    "Comparison 5: Multiple Random Accesses": [
        (100, 2.05, 13.06),
        (1000, 16.01, 1.27),
        (2000, 33.64, 0.67434),
    ],
}

def estimate_crossover(ops_list, v1_times, v2_times):
    """Estimate the operation count where V1 and V2 times are equal"""
    # Convert to numpy arrays
    ops = np.array(ops_list)
    v1 = np.array(v1_times)
    v2 = np.array(v2_times)
    # Find where V1 crosses V2 (where V1 - V2 = 0)
    diff = v1 - v2
    # Check if there's a sign change (crossover in the data)
    if len(diff) >= 2:
        # Check if difference changes sign
        sign_changes = []
        for i in range(len(diff) - 1):
            if diff[i] * diff[i+1] <= 0:  # Sign change or zero
                # Linear interpolation between points
                x1, x2 = ops[i], ops[i+1]
                y1, y2 = diff[i], diff[i+1]
                if y2 != y1:
                    # Linear interpolation: y = y1 + (y2-y1)*(x-x1)/(x2-x1)
                    # Find x where y = 0
                    crossover = x1 - y1 * (x2 - x1) / (y2 - y1)
                    if x1 <= crossover <= x2:
                        return crossover
        # If no sign change, extrapolate using linear fit
        if len(ops) >= 2:
            # Fit linear model to the difference
            coeffs = np.polyfit(ops, diff, 1)
            # Find where diff = 0: 0 = a*x + b => x = -b/a
            if abs(coeffs[0]) > 1e-10:  # Avoid division by zero
                crossover = -coeffs[1] / coeffs[0]
                # Only return if it's in a reasonable range
                if 0 < crossover < 10000:
                    return crossover
    return None

def analyze_comparison(name, points):
    """Analyze a single comparison"""
    ops_list = [p[0] for p in points]
    v1_times = [p[1] for p in points]
    v2_times = [p[2] for p in points]
    print(f"\n{name}:")
    print(f"  Operations: {ops_list}")
    print(f"  V1 times (ms): {[f'{t:.2f}' for t in v1_times]}")
    print(f"  V2 times (ms): {[f'{t:.2f}' for t in v2_times]}")
    # Calculate ratios
    ratios = [v1/v2 if v2 > 0 else float('inf') for v1, v2 in zip(v1_times, v2_times)]
    print(f"  V1/V2 ratios: {[f'{r:.2f}x' for r in ratios]}")
    # Estimate crossover
    crossover = estimate_crossover(ops_list, v1_times, v2_times)
    if crossover:
        print(f"  Estimated crossover: ~{int(crossover)} operations")
    else:
        # Check if V2 is always faster or always slower
        if all(v1 > v2 for v1, v2 in zip(v1_times, v2_times)):
            print(f"  V2 is always faster (no crossover)")
        elif all(v1 < v2 for v1, v2 in zip(v1_times, v2_times)):
            print(f"  V2 is always slower (no crossover)")
        else:
            print(f"  Crossover point unclear")
    # Linear extrapolation for next points
    if len(ops_list) >= 2:
        # Fit V1: typically increases with ops (degradation)
        v1_coeffs = np.polyfit(ops_list, v1_times, 1)
        # Fit V2: typically stable or decreases slightly
        v2_coeffs = np.polyfit(ops_list, v2_times, 1)
        print(f"  V1 trend: {v1_coeffs[0]:.4f}*ops + {v1_coeffs[1]:.4f}")
        print(f"  V2 trend: {v2_coeffs[0]:.4f}*ops + {v2_coeffs[1]:.4f}")
        # Predict at 3000, 4000, 5000
        for test_ops in [3000, 4000, 5000]:
            v1_pred = v1_coeffs[0] * test_ops + v1_coeffs[1]
            v2_pred = v2_coeffs[0] * test_ops + v2_coeffs[1]
            ratio = v1_pred / v2_pred if v2_pred > 0 else float('inf')
            print(f"  Predicted at {test_ops} ops: V1={v1_pred:.2f}ms, V2={v2_pred:.2f}ms, ratio={ratio:.2f}x")
    return crossover

def main():
    print("="*70)
    print("V1 vs V2 PERFORMANCE CROSSOVER ANALYSIS")
    print("="*70)
    crossovers = []
    for name, points in data.items():
        crossover = analyze_comparison(name, points)
        if crossover:
            crossovers.append((name, crossover))
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    if crossovers:
        print("\nEstimated crossover points (V1 = V2):")
        for name, crossover in crossovers:
            print(f"  {name}: ~{int(crossover)} operations")
        avg_crossover = np.mean([c for _, c in crossovers])
        print(f"\nAverage crossover point: ~{int(avg_crossover)} operations")
        print(f"Median crossover point: ~{int(np.median([c for _, c in crossovers]))} operations")
    else:
        print("\nNo clear crossover points found in the data range.")
        print("V2 appears to become faster than V1 between 100 and 1000 operations.")
    print("\n" + "="*70)
    print("KEY OBSERVATIONS")
    print("="*70)
    print("""
1. At 100 operations: V2 is slower (0.12-0.16x of V1 speed)
2. At 1000 operations: V2 is much faster (12-13x faster than V1)
3. At 2000 operations: V2 is even faster (37-60x faster than V1)
The crossover appears to occur between 100 and 1000 operations, likely around:
  - 200-400 operations for most comparisons
  - Paging (Comparison 4) behaves differently and may not cross over
V1 performance degrades significantly with more operations (likely due to repeated
full file scans), while V2 maintains consistent performance (indexed access).
    """)
if __name__ == "__main__":
    main()
