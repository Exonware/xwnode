#!/usr/bin/env python3
"""
Parse comparison results and generate recommendation table
"""

import re
from pathlib import Path

def parse_results_file(file_path):
    """Parse the comparison results file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Extract data for each comparison and operation count
    results = {}
    # Pattern to match: "RUNNING ALL COMPARISONS - {num_ops} OPERATIONS"
    # Then find each comparison section
    pattern = r'RUNNING ALL COMPARISONS - (\d+) OPERATIONS.*?(?=RUNNING ALL COMPARISONS|\Z)'
    for match in re.finditer(pattern, content, re.DOTALL):
        num_ops = int(match.group(1))
        section = match.group(0)
        # Extract each comparison
        comparisons = {
            'First Access': extract_comparison(section, 'COMPARISON 1: First Access'),
            'Random ID Access': extract_comparison(section, 'COMPARISON 2: Random ID Access'),
            'ID-Based Lookup': extract_comparison(section, 'COMPARISON 3: ID-Based Lookup'),
            'Paging': extract_comparison(section, 'COMPARISON 4: Paging'),
            'Multiple Random Accesses': extract_comparison(section, 'COMPARISON 5: Multiple Random Accesses'),
        }
        results[num_ops] = comparisons
    return results

def extract_comparison(section, comparison_name):
    """Extract V1 and V2 performance data from a comparison section"""
    # Find the comparison section
    pattern = rf'{re.escape(comparison_name)}.*?(?=COMPARISON \d+:|COMPLETED|\Z)'
    match = re.search(pattern, section, re.DOTALL)
    if not match:
        return None
    comp_section = match.group(0)
    # Extract V1 avg time
    v1_pattern = r'V1.*?Avg per (?:op|access):\s*([\d.]+)\s*(µs|ms|s)'
    v1_match = re.search(v1_pattern, comp_section)
    v1_time = None
    if v1_match:
        value = float(v1_match.group(1))
        unit = v1_match.group(2)
        # Convert to ms
        if unit == 'µs':
            v1_time = value / 1000
        elif unit == 'ms':
            v1_time = value
        elif unit == 's':
            v1_time = value * 1000
    # Extract V2 Warm avg time
    v2_pattern = r'V2.*?RUN 2.*?Avg per (?:op|access):\s*([\d.]+)\s*(µs|ms|s)'
    v2_match = re.search(v2_pattern, comp_section)
    v2_time = None
    if v2_match:
        value = float(v2_match.group(1))
        unit = v2_match.group(2)
        # Convert to ms
        if unit == 'µs':
            v2_time = value / 1000
        elif unit == 'ms':
            v2_time = value
        elif unit == 's':
            v2_time = value * 1000
    # Extract speedup ratio
    speedup_pattern = r'V2 Warm is ([\d.]+)x (faster|slower) than V1'
    speedup_match = re.search(speedup_pattern, comp_section)
    speedup = None
    if speedup_match:
        speedup = float(speedup_match.group(1))
        if speedup_match.group(2) == 'slower':
            speedup = 1.0 / speedup
    return {
        'v1_time_ms': v1_time,
        'v2_time_ms': v2_time,
        'speedup': speedup
    }

def generate_recommendation_table(results):
    """Generate recommendation table"""
    # Get all operation counts
    op_counts = sorted(results.keys())
    # Get all comparison types
    comparison_types = ['First Access', 'Random ID Access', 'ID-Based Lookup', 'Paging', 'Multiple Random Accesses']
    # Build table
    table_rows = []
    table_rows.append("| Operations | First Access | Random ID Access | ID-Based Lookup | Paging | Multiple Random Accesses |")
    table_rows.append("|------------|--------------|------------------|-----------------|---------|--------------------------|")
    for num_ops in op_counts:
        row = [f"{num_ops}"]
        for comp_type in comparison_types:
            comp_data = results[num_ops].get(comp_type)
            if comp_data and comp_data.get('speedup'):
                speedup = comp_data['speedup']
                if speedup > 1.1:  # V2 is significantly faster
                    recommendation = "**V2**"
                elif speedup < 0.9:  # V1 is significantly faster
                    recommendation = "**V1**"
                else:  # Comparable
                    recommendation = "V1≈V2"
            else:
                recommendation = "N/A"
            row.append(recommendation)
        table_rows.append("| " + " | ".join(row) + " |")
    return "\n".join(table_rows)

def generate_detailed_table(results):
    """Generate detailed table with actual times"""
    op_counts = sorted(results.keys())
    comparison_types = ['First Access', 'Random ID Access', 'ID-Based Lookup', 'Paging', 'Multiple Random Accesses']
    table_rows = []
    table_rows.append("| Operations | Comparison | V1 Time (ms) | V2 Time (ms) | Speedup | Recommendation |")
    table_rows.append("|------------|-----------|--------------|-------------|---------|----------------|")
    for num_ops in op_counts:
        for comp_type in comparison_types:
            comp_data = results[num_ops].get(comp_type)
            if comp_data:
                v1_time = comp_data.get('v1_time_ms', 'N/A')
                v2_time = comp_data.get('v2_time_ms', 'N/A')
                speedup = comp_data.get('speedup', 'N/A')
                if isinstance(speedup, float):
                    if speedup > 1.1:
                        rec = "**V2**"
                    elif speedup < 0.9:
                        rec = "**V1**"
                    else:
                        rec = "V1≈V2"
                else:
                    rec = "N/A"
                v1_str = f"{v1_time:.3f}" if isinstance(v1_time, float) else str(v1_time)
                v2_str = f"{v2_time:.3f}" if isinstance(v2_time, float) else str(v2_time)
                speedup_str = f"{speedup:.2f}x" if isinstance(speedup, float) else str(speedup)
                table_rows.append(f"| {num_ops} | {comp_type} | {v1_str} | {v2_str} | {speedup_str} | {rec} |")
    return "\n".join(table_rows)

def main():
    results_file = Path(__file__).parent / "comparison_results.txt"
    output_file = Path(__file__).parent / "RECOMMENDATIONS.md"
    print("Parsing results...")
    results = parse_results_file(results_file)
    print(f"Found results for {len(results)} operation counts")
    # Read the full terminal output
    with open(results_file, 'r', encoding='utf-8') as f:
        terminal_output = f.read()
    # Generate tables first
    quick_table = generate_recommendation_table(results)
    detailed_table = generate_detailed_table(results)
    # Generate markdown
    md_content = f"""# JSON Utils V1 vs V2 Performance Recommendations
## Quick Reference Table
Based on performance testing with various operation counts, here are the recommendations for when to use V1 (Streaming) vs V2 (Indexed):
{quick_table}
### Legend
- **V1**: Use V1 (Streaming) - Better performance
- **V2**: Use V2 (Indexed) - Better performance  
- **V1≈V2**: Comparable performance - either is fine
## Detailed Performance Data
{detailed_table}
## Key Insights
1. **Crossover Point**: V2 becomes faster than V1 around **400-500 operations** for most comparisons
2. **Paging Exception**: Paging operations favor V1 until much higher operation counts (~1800+ operations)
3. **V1 Advantage**: V1 is better for small operation counts (< 400) due to lower overhead
4. **V2 Advantage**: V2 scales much better with higher operation counts due to indexed access
## Recommendations by Use Case
### Use V1 (Streaming) when:
- Performing < 400 operations
- One-time or infrequent operations
- Memory footprint is critical
- Paging operations with < 1800 operations
### Use V2 (Indexed) when:
- Performing > 500 operations
- Multiple accesses to the same file
- Random access patterns
- ID-based lookups at scale
- Index can be built once and reused
## Full Terminal Output
<details>
<summary>Click to expand full test results</summary>
```
{terminal_output}
```
</details>
---
*Generated from performance comparison tests*
"""
    # Fix the table generation calls
    md_content = md_content.replace(
        "{table_generate_recommendation_table(results)}",
        generate_recommendation_table(results)
    )
    md_content = md_content.replace(
        "{table_generate_detailed_table(results)}",
        generate_detailed_table(results)
    )
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✅ Generated recommendations file: {output_file}")
if __name__ == "__main__":
    main()
