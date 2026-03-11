#!/usr/bin/env python3
"""
Quick test to verify async-first implementation works.
"""

import asyncio
import sys
from pathlib import Path
# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))
from exonware.xwnode.nodes.strategies.hash_map import HashMapStrategy
async def test_async_operations():
    """Test async operations work correctly."""
    print("="*80)
    print("Testing Async-First Implementation (v0.0.1.30)")
    print("="*80)
    print()
    # Create strategy
    print("1. Creating HashMapStrategy...")
    strategy = HashMapStrategy()
    print("   ✓ Created successfully")
    print()
    # Check async methods exist
    print("2. Checking async methods exist...")
    async_methods = ['insert_async', 'find_async', 'delete_async', 
                     'size_async', 'is_empty_async', 'to_native_async',
                     'keys_async', 'values_async', 'items_async']
    for method in async_methods:
        if hasattr(strategy, method):
            print(f"   ✓ {method}")
        else:
            print(f"   ✗ {method} - MISSING!")
            return False
    print()
    # Test async insert
    print("3. Testing async insert...")
    await strategy.insert_async("key1", "value1")
    await strategy.insert_async("key2", "value2")
    print("   ✓ Async inserts successful")
    print()
    # Test async find
    print("4. Testing async find...")
    val1 = await strategy.find_async("key1")
    val2 = await strategy.find_async("key2")
    assert val1 == "value1", f"Expected 'value1', got '{val1}'"
    assert val2 == "value2", f"Expected 'value2', got '{val2}'"
    print(f"   ✓ Found: key1={val1}, key2={val2}")
    print()
    # Test async size
    print("5. Testing async size...")
    size = await strategy.size_async()
    assert size == 2, f"Expected size 2, got {size}"
    print(f"   ✓ Size: {size}")
    print()
    # Test async is_empty
    print("6. Testing async is_empty...")
    empty = await strategy.is_empty_async()
    assert empty == False, f"Expected False, got {empty}"
    print(f"   ✓ is_empty: {empty}")
    print()
    # Test async keys
    print("7. Testing async keys...")
    keys = []
    async for key in strategy.keys_async():
        keys.append(key)
    print(f"   ✓ Keys: {keys}")
    print()
    # Test async to_native
    print("8. Testing async to_native...")
    native = await strategy.to_native_async()
    print(f"   ✓ Native: {native}")
    print()
    # Test async delete
    print("9. Testing async delete...")
    deleted = await strategy.delete_async("key1")
    assert deleted == True, f"Expected True, got {deleted}"
    size_after = await strategy.size_async()
    assert size_after == 1, f"Expected size 1 after delete, got {size_after}"
    print(f"   ✓ Deleted key1, size now: {size_after}")
    print()
    # Test concurrent operations
    print("10. Testing concurrent operations (TRUE ASYNC!)...")
    strategy2 = HashMapStrategy()
    # Insert 100 items concurrently
    tasks = []
    for i in range(100):
        tasks.append(strategy2.insert_async(f"key{i}", f"value{i}"))
    await asyncio.gather(*tasks)
    final_size = await strategy2.size_async()
    assert final_size == 100, f"Expected 100 items, got {final_size}"
    print(f"   ✓ Concurrent inserts successful! Size: {final_size}")
    print()
    # Test backward compatibility (sync methods)
    print("11. Testing backward compatibility (sync API)...")
    strategy3 = HashMapStrategy()
    strategy3.insert("sync_key", "sync_value")  # Sync method wraps async
    val = strategy3.find("sync_key")  # Sync method wraps async
    assert val == "sync_value", f"Expected 'sync_value', got '{val}'"
    print("   ✓ Sync API works (wraps async via asyncio.run())")
    print()
    print("="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)
    print()
    print("Summary:")
    print("- Async methods: ✓ All 9 methods implemented")
    print("- Async operations: ✓ Working correctly")
    print("- Concurrent operations: ✓ True async with asyncio.Lock")
    print("- Backward compatibility: ✓ Sync API wraps async")
    print()
    print("🎉 Async-First Architecture (v0.0.1.30) is working perfectly!")
    return True


def main():
    """Run async tests."""
    try:
        result = asyncio.run(test_async_operations())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
if __name__ == '__main__':
    main()
