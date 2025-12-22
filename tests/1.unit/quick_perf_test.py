#!/usr/bin/env python3
"""Quick performance test - v28 sync vs v30 async."""
import sys
from pathlib import Path
import time
import asyncio

src = Path(__file__).parent / "src"
sys.path.insert(0, str(src))

from exonware.xwnode.nodes.strategies.hash_map import HashMapStrategy

print("="*60)
print("Quick Performance Test: v28 vs v30")
print("="*60, flush=True)

# Test 1: Sync Sequential (v28 style)
print("\n1. Sync Sequential (100 ops)...", flush=True)
s = HashMapStrategy()
start = time.perf_counter()
for i in range(100):
    s.insert(f"k{i}", f"v{i}")
    s.find(f"k{i}")
    s.delete(f"k{i}")
sync_time = time.perf_counter() - start
print(f"   Time: {sync_time*1000:.2f}ms", flush=True)

# Test 2: Async Sequential (v30 no concurrency)
print("\n2. Async Sequential (100 ops)...", flush=True)
async def async_seq():
    s = HashMapStrategy()
    for i in range(100):
        await s.insert_async(f"k{i}", f"v{i}")
        await s.find_async(f"k{i}")
        await s.delete_async(f"k{i}")

start = time.perf_counter()
asyncio.run(async_seq())
async_seq_time = time.perf_counter() - start
print(f"   Time: {async_seq_time*1000:.2f}ms", flush=True)
print(f"   Overhead: {(async_seq_time/sync_time-1)*100:+.1f}%", flush=True)

# Test 3: Async Concurrent (v30 TRUE ASYNC)
print("\n3. Async Concurrent (100 ops)...", flush=True)
async def async_conc():
    s = HashMapStrategy()
    await asyncio.gather(*[s.insert_async(f"k{i}", f"v{i}") for i in range(100)])
    await asyncio.gather(*[s.find_async(f"k{i}") for i in range(100)])
    await asyncio.gather(*[s.delete_async(f"k{i}") for i in range(100)])

start = time.perf_counter()
asyncio.run(async_conc())
async_conc_time = time.perf_counter() - start
print(f"   Time: {async_conc_time*1000:.2f}ms", flush=True)
print(f"   SPEEDUP: {sync_time/async_conc_time:.1f}x faster! 🚀", flush=True)

print("\n" + "="*60, flush=True)
print("Summary:", flush=True)
print(f"  Sync:           {sync_time*1000:.2f}ms", flush=True)
print(f"  Async Seq:      {async_seq_time*1000:.2f}ms ({(async_seq_time/sync_time-1)*100:+.1f}%)", flush=True)
print(f"  Async Conc:     {async_conc_time*1000:.2f}ms ({sync_time/async_conc_time:.1f}x faster! ⚡)", flush=True)
print("="*60, flush=True)

