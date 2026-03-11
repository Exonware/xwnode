#!/usr/bin/env python3
"""Simple test from proper package structure."""

import sys
from pathlib import Path
# Add proper src path
src = Path(__file__).parent / 'src'
sys.path.insert(0, str(src))
print("Testing async-first implementation...")
print()
try:
    # Import from proper package
    print("1. Importing HashMapStrategy...")
    from exonware.xwnode.nodes.strategies.hash_map import HashMapStrategy
    print("   ✅ Import successful")
    print("\n2. Creating instance...")
    s = HashMapStrategy()
    print("   ✅ Instance created")
    print("\n3. Checking async methods...")
    methods = ['insert_async', 'find_async', 'delete_async', 'size_async',
               'is_empty_async', 'to_native_async', 'keys_async', 'values_async', 'items_async']
    for m in methods:
        assert hasattr(s, m), f"Missing {m}"
    print(f"   ✅ All 9 async methods present")
    print("\n4. Checking _lock...")
    assert hasattr(s, '_lock'), "Missing _lock"
    print("   ✅ _lock present")
    print("\n5. Testing sync methods (backward compatibility)...")
    s.insert("key1", "value1")
    val = s.find("key1")
    assert val == "value1"
    print("   ✅ Sync methods work")
    print("\n" + "="*60)
    print("✅ ASYNC-FIRST IMPLEMENTATION VERIFIED!")
    print("="*60)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
