# Benchmark log: Archive baseline and LRU_CACHE history

**Date:** 07-Feb-2026  
**Source:** Value extracted from _archive (BENCHMARK_BASELINE_RESULTS, BENCHMARK_*, PERFORMANCE_*, OPTIMIZATION_*)  
**Scope:** Methodology and LRU_CACHE optimization phases

---

## Baseline methodology (from archive)

- **Platform:** Windows 10, Python 3.12 (historical).
- **Nodes:** 1000 iterations per operation (put, get, delete, iteration, size); warmup 100.
- **Edges:** 100 iterations per operation (add_edge, get_neighbors where supported); warmup 10.
- **Metrics:** Mean/median/min/max time (ms), ops/sec, standard deviation.
- **Scripts:** Repo [benchmarks/](../../../benchmarks/), [REF_54_BENCH.md](../../REF_54_BENCH.md).

---

## LRU_CACHE performance history (3 phases)

1. **Phase 1 — Path navigation fix**  
   Before: 1576 ms/op (path navigation + to_native() for LRU_CACHE).  
   After: 0.23 ms/op (direct key-value fast path in facade).  
   **Improvement: ~6800x.**

2. **Phase 2 — Cache infrastructure**  
   Replaced manual OrderedDict usage with shared ACachedStrategy / AKeyValueStrategy; reduced duplication and improved consistency.

3. **Phase 3 — Eviction and tuning**  
   Eviction and cache-size behavior optimized; results used for baseline comparison and regression checks.

---

## Traceability

- **SLA and run logs:** [REF_54_BENCH.md](../../REF_54_BENCH.md), [INDEX.md](INDEX.md).
- **Archive consolidation:** [REVIEW_20260207_ARCHIVE_CONSOLIDATION.md](../reviews/REVIEW_20260207_ARCHIVE_CONSOLIDATION.md).
