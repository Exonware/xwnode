# XWNode Strategy Benchmarks

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com

## Purpose

Benchmark scripts and results for xwnode strategies. Use as a baseline before tuning.
---

## Benchmark Script

### `benchmark_all_strategies.py`

Comprehensive benchmark suite for all node and edge strategies.

**Usage:**

```bash
# Benchmark all strategies (nodes + edges)
cd d:\OneDrive\DEV\exonware
python xwnode/benchmarks/benchmark_all_strategies.py

# Benchmark only nodes
python xwnode/benchmarks/benchmark_all_strategies.py --nodes-only

# Benchmark only edges
python xwnode/benchmarks/benchmark_all_strategies.py --edges-only

# Custom iterations and output directory
python xwnode/benchmarks/benchmark_all_strategies.py --iterations 2000 --output-dir xwnode/benchmarks
```

**Output Files:**
- `node_strategies_baseline.json` - All node strategy results
- `edge_strategies_baseline.json` - All edge strategy results
- `all_strategies_baseline.json` - Combined results with metadata

---

## Results Format

Results are saved as JSON with the following structure:

```json
{
  "nodes": {
    "LRU_CACHE": {
      "mode": "LRU_CACHE",
      "name": "Lru Cache",
      "put_performance": {
        "mean_ms": 0.0012,
        "median_ms": 0.0011,
        "min_ms": 0.0009,
        "max_ms": 0.0034,
        "stdev_ms": 0.0003,
        "ops_per_sec": 833333
      },
      "get_performance": { ... },
      "delete_performance": { ... },
      "iteration_performance": { ... },
      "size_performance": { ... }
    },
    ...
  },
  "edges": {
    "ADJ_LIST": {
      "mode": "ADJ_LIST",
      "name": "Adj List",
      "add_edge_performance": {
        "mean_ms": 0.0056,
        "median_ms": 0.0052,
        "min_ms": 0.0041,
        "max_ms": 0.0123,
        "ops_per_sec": 178571
      },
      "get_neighbors_performance": { ... }
    },
    ...
  },
  "metadata": {
    "iterations": 1000,
    "warmup": 100,
    "timestamp": 1704067200.0
  }
}
```

---

## Related Documents

- [../docs/BENCHMARK_BASELINE_RESULTS.md](../docs/BENCHMARK_BASELINE_RESULTS.md) - Baseline results documentation
- [../docs/STRATEGY_OPTIMIZATION_OPPORTUNITIES.md](../docs/STRATEGY_OPTIMIZATION_OPPORTUNITIES.md) - Optimization opportunities
- [../docs/BENCHMARK_ANALYSIS_AND_IMPROVEMENTS.md](../docs/BENCHMARK_ANALYSIS_AND_IMPROVEMENTS.md) - LRU_CACHE optimization results

---

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** connect@exonware.com  
**Version:** 0.0.1.0  
**Generation Date:** 2025-01-XX
